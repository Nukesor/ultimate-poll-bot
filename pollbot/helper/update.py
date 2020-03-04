"""Update or delete poll messages."""
from datetime import datetime
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from telethon.utils import resolve_inline_message_id
from telethon.errors.rpcbaseerrors import (
    ForbiddenError,
)
from telethon.errors.rpcerrorlist import (
    MessageIdInvalidError,
    MessageNotModifiedError,
)
from telethon.tl.types import (
    UpdateInlineBotCallbackQuery,
    InputBotInlineMessageID,
)

from pollbot.i18n import i18n
from pollbot.client import client
from pollbot.models import Update, Reference
from pollbot.telegram.keyboard import get_management_keyboard
from pollbot.helper.enums import ExpectedInput, ReferenceType
from pollbot.display.poll.compilation import get_poll_text_and_vote_keyboard


async def update_poll_messages(session, poll, event=None):
    """Logic for handling updates.

    The message the original call has been made from will be updated instantly.
    The updates on all other messages will be scheduled in the background.
    """
    now = datetime.now()
    if event is not None:
        if isinstance(event.original_update, UpdateInlineBotCallbackQuery):
            # We got a vote from an poll shared via inline query
            message_id = event.original_update.msg_id.id
        else:
            # We got a request from a private chat
            message_id = event.message_id

        reference = session.query(Reference) \
            .filter(Reference.message_id == message_id) \
            .one_or_none()

        # For now until all legacy inline message ids are migrated
        if reference is not None:
            await update_reference(session, poll, reference)

    # Check whether there already is a scheduled update
    new_update = False
    update = session.query(Update) \
        .filter(Update.poll == poll) \
        .one_or_none()

    # If there's no update yet, create a new one
    if update is None:
        try:
            update = Update(poll, now)
            session.add(update)
            session.commit()
            new_update = True
        except (UniqueViolation, IntegrityError):
            # Some other function already created the update
            session.rollback()
            update = session.query(Update) \
                .filter(Update.poll == poll) \
                .one()

    if not new_update:
        # Increase the counter and update the next_update date
        # This will result in a new update in the background job.
        # + The update will be scheduled at the end
        session.query(Update) \
            .filter(Update.poll == poll) \
            .update({
                'count': Update.count + 1,
                'next_update': datetime.now(),
            })


async def send_updates(session, poll, show_warning=False):
    """Actually update all messages."""
    for reference in poll.references:
        await update_reference(session, poll, reference, show_warning)


async def update_reference(session, poll, reference, show_warning=False):
    try:
        # Admin poll management interface
        if reference.type == ReferenceType.admin.name and not poll.in_settings:
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
                reference.user.id,
                message=reference.message_id,
                text=text,
                buttons=keyboard,
                link_preview=False,
            )

        # User that votes in private chat (priority vote)
        elif reference.type == ReferenceType.private_vote.name:
            text, keyboard = get_poll_text_and_vote_keyboard(
                session,
                poll,
                user=reference.user,
                show_warning=show_warning,
            )

            await client.edit_message(
                reference.user.id,
                message=reference.message_id,
                text=text,
                buttons=keyboard,
                link_preview=False,
            )

        # Edit message created via inline query
        elif reference.type == ReferenceType.inline.name:
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
    except ForbiddenError:
        session.delete(reference)
    except ValueError:
        # Could not find input entity
        session.delete(reference)
    except MessageNotModifiedError:
        pass


async def remove_poll_messages(session, poll, remove_all=False):
    """Remove all messages (references) of a poll."""
    if not remove_all:
        poll.closed = True
        await send_updates(session, poll)
        return

    for reference in poll.references:
        try:
            # Admin poll management interface
            if reference.type == ReferenceType.admin.name:
                await client.edit_message(
                    reference.user.id,
                    message=reference.message_id,
                    text=i18n.t('deleted.poll', locale=poll.locale),
                    link_preview=False,
                )

                # User that votes in private chat (priority vote)
            elif reference.type == ReferenceType.private_vote.name:
                await client.edit_message(
                    reference.user.id,
                    message=reference.message_id,
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

        except ForbiddenError:
            session.delete(reference)
        except MessageIdInvalidError:
            session.delete(reference)
        except ValueError:
            # Could not find input entity
            session.delete(reference)
        except MessageNotModifiedError:
            pass


def inline_message_id_from_reference(reference):
    """Helper to create a inline from references and legacy bot api references."""
    if reference.legacy_inline_message_id is not None:
        message_id, peer, dc_id, access_hash = resolve_inline_message_id(reference.legacy_inline_message_id)
        # Migrate from legacy to new format
        reference.message_id = message_id
        reference.message_dc_id = dc_id
        reference.message_access_hash = access_hash
        reference.legacy_inline_message_id = None
        return InputBotInlineMessageID(
            int(dc_id),
            int(message_id),
            int(access_hash)
        )

    else:
        return InputBotInlineMessageID(
            reference.message_dc_id,
            reference.message_id,
            reference.message_access_hash,
        )
