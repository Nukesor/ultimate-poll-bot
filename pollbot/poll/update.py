"""Update or delete poll messages."""
from datetime import datetime, timedelta
from typing import Optional

from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.orm.scoping import scoped_session
from telegram.bot import Bot
from telegram.error import BadRequest, RetryAfter, TimedOut, Unauthorized

from pollbot.display.poll.compilation import get_poll_text_and_vote_keyboard
from pollbot.enums import ExpectedInput, ReferenceType
from pollbot.models import Reference, Update
from pollbot.models.poll import Poll
from pollbot.models.user import User
from pollbot.telegram.keyboard.management import get_management_keyboard


def update_poll_messages(
    session: scoped_session,
    bot: Bot,
    poll: Poll,
    message_id: Optional[int] = None,
    user: Optional[User] = None,
    inline_message_id: Optional[str] = None,
) -> None:
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
            .filter(Reference.poll == poll)
            .one_or_none()
        )
    elif inline_message_id is not None:
        reference = (
            session.query(Reference)
            .filter(Reference.bot_inline_message_id == inline_message_id)
            .filter(Reference.poll == poll)
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
            # Some other function already created the update. Try again
            session.rollback()
            update_poll_messages(session, bot, poll)

    if not new_update:
        # In case there already is an update increase the counter and set the next_update date
        # This will result in a new update in the background job and ensures that
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
            # Anyway just try again
            update_poll_messages(session, bot, poll)


def send_updates(session: scoped_session, bot: Bot, poll: Poll) -> None:
    """Actually update all messages."""
    for reference in poll.references:
        update_reference(session, bot, poll, reference)


def try_update_reference(
    session: scoped_session,
    bot: Bot,
    poll: Poll,
    reference: Reference,
    first_try: bool = False,
) -> None:
    try:
        update_reference(session, bot, poll, reference, first_try)
        session.commit()
    except RetryAfter as e:
        session.rollback()
        # Handle a flood control exception on initial reference update.
        retry_after_seconds = int(e.retry_after) + 1
        retry_after = datetime.now() + timedelta(seconds=retry_after_seconds)
        update = Update(poll, retry_after)
        try:
            session.add(update)
            session.commit()
        except IntegrityError:
            # There's already a scheduled update for this poll.
            session.rollback()

    except IntegrityError:
        # There's already a scheduled update for this poll.
        session.rollback()


def update_reference(
    session: scoped_session,
    bot: Bot,
    poll: Poll,
    reference: Reference,
    first_try: bool = False,
) -> None:
    try:
        # Admin poll management interface
        if reference.type == ReferenceType.admin.name and not poll.in_settings:
            text, keyboard = get_poll_text_and_vote_keyboard(
                session, poll, user=poll.user, show_back=True
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
                session,
                poll,
                user=reference.user,
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
            text, keyboard = get_poll_text_and_vote_keyboard(session, poll)

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
            # Sometimes it fells like we're too fast and the message isn't synced between Telegram's servers yet.
            # If this happens, allow the first try to fail and schedule an update.
            # If it happens again, the reference will be removed on the second try.
            if first_try:
                update = Update(poll, datetime.now() + timedelta(seconds=5))
                session.add(update)

                return

            session.delete(reference)
            session.flush()
        elif e.message.startswith("Message is not modified") or e.message.startswith(
            "Message_author_required"
        ):
            pass
        else:
            raise e

    except Unauthorized:
        session.delete(reference)
        session.flush()
    except TimedOut:
        # Ignore timeouts during updates for now
        pass
