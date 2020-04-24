"""Update or delete poll messages."""
from datetime import datetime, timedelta
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import ObjectDeletedError
from telegram.error import BadRequest, RetryAfter, Unauthorized, TimedOut

from pollbot.i18n import i18n
from pollbot.models import Update, Reference
from pollbot.telegram.keyboard import get_management_keyboard
from pollbot.helper.enums import ExpectedInput, ReferenceType
from pollbot.display.poll.compilation import get_poll_text_and_vote_keyboard


def update_poll_messages(
    session, bot, poll, message_id=None, user=None, inline_message_id=None
):
    """Logic for handling updates.

    The message the original call has been made from will be updated instantly.
    The updates on all other messages will be scheduled in the background.
    """
    now = datetime.now()
    reference = None
    if message_id is not None:
        reference = (
            session.query(Reference)
            .filter(Reference.message_id == message_id)
            .filter(Reference.user == user)
            .one_or_none()
        )
    elif inline_message_id is not None:
        reference = (
            session.query(Reference)
            .filter(Reference.bot_inline_message_id == inline_message_id)
            .one_or_none()
        )

    # Check whether there already is a scheduled update
    new_update = False
    retry_after = None
    update = session.query(Update).filter(Update.poll == poll).one_or_none()

    if reference is not None:
        try:
            update_reference(session, bot, poll, reference)
        except RetryAfter as e:
            retry_after = int(e.retry_after) + 1
            retry_after = datetime.now() + timedelta(seconds=retry_after)
            pass

    # If there's no update yet, create a new one
    if update is None:
        try:
            update = Update(poll, now)
            session.add(update)
            if retry_after is not None:
                update.next_update = retry_after

            session.commit()
            new_update = True
        except (UniqueViolation, IntegrityError):
            # Some other function already created the update
            session.rollback()
            update = session.query(Update).filter(Update.poll == poll).one()

    if not new_update:
        # In case there already is an update increase the counter and set the next_update date
        # This will result in a new update in the background job and ensures
        # currently (right now) running updates will be scheduled again.
        if retry_after is not None:
            next_update = retry_after
        else:
            next_update = datetime.now()

        try:
            session.query(Update).filter(Update.poll == poll).update(
                {"count": Update.count + 1, "next_update": next_update}
            )
        except ObjectDeletedError:
            # This is a hard edge-case
            # This occurs, if the update we got a few microseconds ago
            # just got deleted by the background job. It happens maybe
            # once every 10000 requests and fixes itself as soon as somebody
            # votes on the poll once more
            #
            # The result of this MAY be, that polls in other chats have a
            # desync of a single vote. But it may also be the case, that
            # everything is already in sync.
            session.rollback()
            pass


def send_updates(session, bot, poll, show_warning=False):
    """Actually update all messages."""
    for reference in poll.references:
        update_reference(session, bot, poll, reference, show_warning)


def update_reference(session, bot, poll, reference, show_warning=False):
    try:
        # Admin poll management interface
        if reference.type == ReferenceType.admin.name and not poll.in_settings:
            text, keyboard = get_poll_text_and_vote_keyboard(
                session, poll, user=poll.user, show_warning=show_warning, show_back=True
            )

            if poll.user.expected_input != ExpectedInput.votes.name:
                keyboard = get_management_keyboard(poll)

            bot.edit_message_text(
                text,
                chat_id=reference.user.id,
                message_id=reference.message_id,
                reply_markup=keyboard,
                parse_mode="markdown",
                disable_web_page_preview=True,
            )

        # User that votes in private chat (priority vote)
        elif reference.type == ReferenceType.private_vote.name:
            text, keyboard = get_poll_text_and_vote_keyboard(
                session, poll, user=reference.user, show_warning=show_warning,
            )

            bot.edit_message_text(
                text,
                chat_id=reference.user.id,
                message_id=reference.message_id,
                reply_markup=keyboard,
                parse_mode="markdown",
                disable_web_page_preview=True,
            )

        # Edit message created via inline query
        elif reference.type == ReferenceType.inline.name:
            # Create text and keyboard
            text, keyboard = get_poll_text_and_vote_keyboard(
                session, poll, show_warning=show_warning
            )

            bot.edit_message_text(
                text,
                inline_message_id=reference.bot_inline_message_id,
                reply_markup=keyboard,
                parse_mode="markdown",
                disable_web_page_preview=True,
            )

    except BadRequest as e:
        if (
            e.message.startswith("Message_id_invalid")
            or e.message.startswith("Message can't be edited")
            or e.message.startswith("Message to edit not found")
            or e.message.startswith("Chat not found")
            or e.message.startswith("Can't access the chat")
        ):
            session.delete(reference)
            session.commit()
        elif e.message.startswith("Message is not modified"):
            pass
        else:
            raise

    except Unauthorized as e:
        session.delete(reference)
        session.commit()
    except TimedOut:
        # Ignore timeouts during updates for now
        pass


def remove_poll_messages(session, bot, poll, remove_all=False):
    """Remove all messages (references) of a poll."""
    if not remove_all:
        poll.closed = True
        send_updates(session, bot, poll)
        return

    for reference in poll.references:
        try:
            # 1. Admin poll management interface
            # 2. User that votes in private chat (priority vote)
            if reference.type in [
                ReferenceType.admin.name,
                ReferenceType.private_vote.name,
            ]:
                bot.edit_message_text(
                    i18n.t("deleted.poll", locale=poll.locale),
                    chat_id=reference.user.id,
                    message_id=reference.message_id,
                )

            # Remove message created via inline_message_id
            else:
                bot.edit_message_text(
                    i18n.t("deleted.poll", locale=poll.locale),
                    inline_message_id=reference.bot_inline_message_id,
                )

        except BadRequest as e:
            if e.message.startswith("Message_id_invalid") or e.message.startswith(
                "Message to edit not found"
            ):
                pass
            else:
                raise
