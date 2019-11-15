"""Update or delete poll messages."""
from datetime import datetime, timedelta
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from telegram.error import BadRequest, RetryAfter, Unauthorized

from pollbot.i18n import i18n
from pollbot.telegram.keyboard import get_management_keyboard
from pollbot.helper.enums import ExpectedInput
from pollbot.display import get_poll_text_and_vote_keyboard
from pollbot.models import Update


def update_poll_messages(session, bot, poll):
    """Logic for handling updates."""
    now = datetime.now()
    # Check whether we have a new window
    current_update = session.query(Update) \
        .filter(Update.poll == poll) \
        .one_or_none()

    # Don't handle it in here, it's already handled in the job
    if current_update is not None:
        return

    try:
        # Try to send updates
        send_updates(session, bot, poll)
    except RetryAfter as e:
        # Schedule an update after the RetryAfter timeout + 1 second buffer
        try:
            update = Update(poll, now + timedelta(seconds=int(e.retry_after) + 1))
            session.add(update)
            session.commit()
        except (UniqueViolation, IntegrityError):
            session.rollback()

    except Exception:
        # Something happened
        # Schedule an update after two secondsj
        try:
            update = Update(poll, now + timedelta(seconds=3))
            session.add(update)
            session.commit()
        except (UniqueViolation, IntegrityError):
            # The update has already been added
            session.rollback()


def send_updates(session, bot, poll, show_warning=False):
    """Actually update all messages."""
    for reference in poll.references:
        try:
            # Admin poll management interface
            if reference.admin_user is not None and not poll.in_settings:
                text, keyboard = get_poll_text_and_vote_keyboard(
                    session,
                    poll,
                    user=poll.user,
                    show_warning=show_warning,
                    show_back=True
                )

                if poll.user.expected_input != ExpectedInput.votes.name:
                    keyboard = get_management_keyboard(poll)

                try:
                    bot.edit_message_text(
                        text,
                        chat_id=reference.admin_user.id,
                        message_id=reference.admin_message_id,
                        reply_markup=keyboard,
                        parse_mode='markdown',
                        disable_web_page_preview=True,
                    )
                except Unauthorized as e:
                    if e.message == 'Forbidden: user is deactivated':
                        session.delete(reference)

            elif reference.vote_user is not None:
                text, keyboard = get_poll_text_and_vote_keyboard(
                    session,
                    poll,
                    user=reference.vote_user,
                    show_warning=show_warning,
                )

                try:
                    bot.edit_message_text(
                        text,
                        chat_id=reference.vote_user.id,
                        message_id=reference.vote_message_id,
                        reply_markup=keyboard,
                        parse_mode='markdown',
                        disable_web_page_preview=True,
                    )
                except Unauthorized as e:
                    if e.message == 'Forbidden: user is deactivated':
                        session.delete(reference)


            # Edit message via inline_message_id
            elif reference.inline_message_id is not None:
                # Create text and keyboard
                text, keyboard = get_poll_text_and_vote_keyboard(session, poll, show_warning=show_warning)

                bot.edit_message_text(
                    text,
                    inline_message_id=reference.inline_message_id,
                    reply_markup=keyboard,
                    parse_mode='markdown',
                    disable_web_page_preview=True,
                )
        except BadRequest as e:
            if e.message.startswith('Message_id_invalid') or \
                   e.message.startswith("Message can't be edited") or \
                   e.message.startswith("Message to edit not found") or \
                   e.message.startswith("Chat not found"):
                session.delete(reference)
                session.commit()
            elif e.message.startswith('Message is not modified'):
                pass
            else:
                raise


def remove_poll_messages(session, bot, poll, remove_all=False):
    """Remove all messages (references) of a poll."""
    if not remove_all:
        poll.closed = True
        send_updates(session, bot, poll)

    for reference in poll.references:
        try:
            # Admin poll management interface
            if reference.inline_message_id is None:
                bot.edit_message_text(
                    i18n.t('deleted.poll', locale=poll.locale),
                    chat_id=reference.admin_user.id,
                    message_id=reference.admin_message_id,
                )

            # Remove message created via inline_message_id
            elif remove_all:
                bot.edit_message_text(
                    i18n.t('deleted.poll', locale=poll.locale),
                    inline_message_id=reference.inline_message_id,
                )

        except BadRequest as e:
            if e.message.startswith('Message_id_invalid') or \
                   e.message.startswith("Message to edit not found"):
                pass
            else:
                raise
