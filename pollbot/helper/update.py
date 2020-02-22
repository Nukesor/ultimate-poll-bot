"""Update or delete poll messages."""
from datetime import datetime, timedelta
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from pollbot.i18n import i18n
from pollbot.client import client
from pollbot.telegram.keyboard import get_management_keyboard
from pollbot.helper.enums import ExpectedInput
from pollbot.display.poll.compilation import get_poll_text_and_vote_keyboard
from pollbot.models import Update


def update_poll_messages(session, poll):
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
        send_updates(session, poll)
#    except (TimedOut, RetryAfter) as e:
#        # Schedule an update after the RetryAfter timeout + 1 second buffer
#        if isinstance(e, RetryAfter):
#            retry_after = int(e.retry_after) + 1
#        else:
#            retry_after = 2
#
#        try:
#            update = Update(poll, now + timedelta(seconds=retry_after))
#            session.add(update)
#            session.commit()
#        except (UniqueViolation, IntegrityError):
#            session.rollback()

    except Exception as e:
        # We encountered an unknown error
        # Since we don't want to continuously tro to send this update, and spam sentry, delete the update
        if current_update is not None:
            session.delete(current_update)
        session.commit()

        raise e


def send_updates(session, poll, show_warning=False):
    """Actually update all messages."""
    for reference in poll.references:
#        try:
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
                client.edit_message(
                    reference.admin_user.id,
                    message=reference.admin_message_id,
                    text=text,
                    buttons=keyboard,
                    link_preview=False,
                )
            except Unauthorized as e:
                if e.message == 'Forbidden: user is deactivated':
                    session.delete(reference)

        # User that votes in private chat (priority vote)
        elif reference.vote_user is not None:
            text, keyboard = get_poll_text_and_vote_keyboard(
                session,
                poll,
                user=reference.vote_user,
                show_warning=show_warning,
            )

            try:
                client.edit_message(
                    reference.vote_user.id,
                    message=reference.vote_message_id,
                    text=text,
                    buttons=keyboard,
                    link_preview=False,
                )

            except Unauthorized as e:
                if e.message == 'Forbidden: user is deactivated':
                    session.delete(reference)

        # Edit message created via inline query
        elif reference.inline_message_id is not None:
            # Create text and keyboard
            text, keyboard = get_poll_text_and_vote_keyboard(session, poll, show_warning=show_warning)

            client.edit_message(
                reference.inline_message_id,
                text=text,
                buttons=keyboard,
                link_preview=False,
            )
#        except BadRequest as e:
#            if e.message.startswith('Message_id_invalid') or \
#                   e.message.startswith("Message can't be edited") or \
#                   e.message.startswith("Message to edit not found") or \
#                   e.message.startswith("Chat not found"):
#                session.delete(reference)
#                session.commit()
#            elif e.message.startswith('Message is not modified'):
#                pass
#            else:
#                raise
#
#        except Unauthorized as e:
#            if e.message.startswith("Forbidden: MESSAGE_AUTHOR_REQUIRED"):
#                session.delete(reference)
#                session.commit()
#            else:
#                raise


def remove_poll_messages(session, poll, remove_all=False):
    """Remove all messages (references) of a poll."""
    if not remove_all:
        poll.closed = True
        send_updates(session, poll)

    for reference in poll.references:
        #        try:
        # Admin poll management interface
        if reference.admin_user is not None:
            client.edit_message(
                reference.admin_user.id,
                message=reference.admin_message_id,
                text=i18n.t('deleted.poll', locale=poll.locale),
            )

            # User that votes in private chat (priority vote)
        elif reference.vote_user is not None:
            client.edit_message(
                reference.vote_user.id,
                message=reference.vote_message_id,
                text=i18n.t('deleted.poll', locale=poll.locale),
            )

            # Remove message created via inline_message_id
        elif remove_all:
            client.edit_message(
                reference.inline_message_id,
                text=i18n.t('deleted.poll', locale=poll.locale),
            )

#        except BadRequest as e:
#            if e.message.startswith('Message_id_invalid') or \
        #                   e.message.startswith("Message to edit not found"):
#                pass
#            else:
#                raise
