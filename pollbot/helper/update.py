"""Update or delete poll messages."""
from datetime import datetime, timedelta
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from telethon.tl.types import InputBotInlineMessageID
from telethon.utils import resolve_inline_message_id
from telethon.errors.rpcerrorlist import (
    MessageIdInvalidError,
)
from telethon.errors.rpcerrorlist import (
    MessageNotModifiedError,
)

from pollbot.i18n import i18n
from pollbot.client import client
from pollbot.telegram.keyboard import get_management_keyboard
from pollbot.helper.enums import ExpectedInput
from pollbot.display.poll.compilation import get_poll_text_and_vote_keyboard
from pollbot.models import Update


async def update_poll_messages(session, poll):
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
        await send_updates(session, poll)
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


async def send_updates(session, poll, show_warning=False):
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

                await client.edit_message(
                    reference.admin_user.id,
                    message=reference.admin_message_id,
                    text=text,
                    buttons=keyboard,
                    link_preview=False,
                )

            # User that votes in private chat (priority vote)
            elif reference.vote_user is not None:
                text, keyboard = get_poll_text_and_vote_keyboard(
                    session,
                    poll,
                    user=reference.vote_user,
                    show_warning=show_warning,
                )

                await client.edit_message(
                    reference.vote_user.id,
                    message=reference.vote_message_id,
                    text=text,
                    buttons=keyboard,
                    link_preview=False,
                )

            # Edit message created via inline query
            else:
                # Create text and keyboard
                text, keyboard = get_poll_text_and_vote_keyboard(session, poll, show_warning=show_warning)

                message_id = inline_message_id_from_reference(reference)
                await client.edit_message(
                    message_id,
                    text,
                    buttons=keyboard,
                    link_preview=False,
                )

        except MessageIdInvalidError:
            session.delete(reference)
        except MessageNotModifiedError:
            pass
        except Exception as e:
            print(e)

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


async def remove_poll_messages(session, poll, remove_all=False):
    """Remove all messages (references) of a poll."""
    if not remove_all:
        poll.closed = True
        await send_updates(session, poll)
        return

    for reference in poll.references:
        try:
            # Admin poll management interface
            if reference.admin_user is not None:
                await client.edit_message(
                    reference.admin_user.id,
                    message=reference.admin_message_id,
                    text=i18n.t('deleted.poll', locale=poll.locale),
                    link_preview=False,
                )

                # User that votes in private chat (priority vote)
            elif reference.vote_user is not None:
                await client.edit_message(
                    reference.vote_user.id,
                    message=reference.vote_message_id,
                    text=i18n.t('deleted.poll', locale=poll.locale),
                    link_preview=False,
                )

                # Remove message created via inline_message_id
            else:
                message_id = inline_message_id_from_reference(reference)
                await client.edit_message(
                    message_id,
                    i18n.t('deleted.poll', locale=poll.locale),
                    link_preview=False,
                )

        except MessageIdInvalidError:
            pass
        except MessageNotModifiedError:
            pass

def inline_message_id_from_reference(reference):
    """Helper to create a inline from references and legacy bot api references."""
    if reference.legacy_inline_message_id is not None:
        message_id, peer, dc_id, access_hash = resolve_inline_message_id(reference.legacy_inline_message_id)
        return InputBotInlineMessageID(
            int(dc_id),
            int(message_id),
            int(access_hash)
        )

    else:
        return InputBotInlineMessageID(
            reference.inline_message_dc_id,
            reference.inline_message_id,
            reference.inline_message_access_hash,
        )
