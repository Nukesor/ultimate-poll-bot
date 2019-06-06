"""Update or delete poll messages."""
from telegram.error import BadRequest
from pollbot.telegram.keyboard import get_vote_keyboard, get_management_keyboard
from pollbot.helper.enums import ExpectedInput
from pollbot.helper.display import (
    get_poll_management_text,
    get_poll_text,
)


def update_poll_messages(session, bot, poll):
    """Update all messages (references) of a poll."""
    for reference in poll.references:
        try:
            # Admin poll management interface
            if reference.admin_message_id is not None and not poll.in_options:
                if poll.expected_input == ExpectedInput.votes.name:
                    keyboard = get_vote_keyboard(poll, show_back=True)
                else:
                    keyboard = get_management_keyboard(poll)

                text = get_poll_management_text(session, poll)
                bot.edit_message_text(
                    text,
                    chat_id=reference.admin_chat_id,
                    message_id=reference.admin_message_id,
                    reply_markup=keyboard,
                    parse_mode='markdown',
                )

            # Edit message via inline_message_id
            elif reference.inline_message_id is not None:
                # Create text and keyboard
                text = get_poll_text(session, poll)
                keyboard = get_vote_keyboard(poll)

                bot.edit_message_text(
                    text,
                    inline_message_id=reference.inline_message_id,
                    reply_markup=keyboard,
                    parse_mode='markdown',
                )
        except BadRequest as e:
            if e.message.startswith('Message_id_invalid'):
                session.delete(reference)
                session.commit()
            else:
                raise


def remove_poll_messages(session, bot, poll):
    """Remove all messages (references) of a poll."""
    for reference in poll.references:
        try:
            # Admin poll management interface
            if reference.inline_message_id is None:
                bot.edit_message_text(
                    'This poll has been permanently deleted.',
                    chat_id=reference.admin_chat_id,
                    message_id=reference.admin_message_id,
                )

            # Edit message via inline_message_id
            else:
                # Create text and keyboard
                bot.edit_message_text(
                    'This poll has been permanently deleted.',
                    inline_message_id=reference.inline_message_id,
                )
        except BadRequest as e:
            if e.message.startswith('Message_id_invalid'):
                pass
            else:
                raise
