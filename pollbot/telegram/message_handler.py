"""Handle messages."""
from pollbot.helper.session import session_wrapper
from pollbot.helper.enums import ExpectedInput, VoteType
from pollbot.helper.display import get_settings_text
from pollbot.helper.update import update_poll_messages
from pollbot.telegram.callback_handler.creation import create_poll

from pollbot.helper.creation import (
    next_option,
    add_options,
)
from pollbot.telegram.keyboard import (
    get_settings_keyboard,
    get_open_datepicker_keyboard,
)

from pollbot.models import Reference


@session_wrapper()
def handle_private_text(bot, update, session, user):
    """Read all private messages and the creation of polls."""
    # The user is currently not editing or creating a poll. Just ignore it
    if user.current_poll is None or user.current_poll.expected_input is None:
        return

    text = update.message.text.strip()
    poll = user.current_poll
    chat = update.message.chat
    expected_input = ExpectedInput[user.current_poll.expected_input]

    # Add the name
    if expected_input == ExpectedInput.name:
        poll.name = text
        poll.expected_input = ExpectedInput.description.name
        chat.send_message('Now send me the description')

    # Add the description
    elif expected_input == ExpectedInput.description:
        poll.description = text
        poll.expected_input = ExpectedInput.options.name
        message = 'Now send me the first option (Or send multiple options at once, each option on a new line)'
        chat.send_message(message, reply_markup=get_open_datepicker_keyboard(poll))

    # Add an option to the poll
    elif expected_input == ExpectedInput.options:
        # Multiple options can be sent at once separated by newline
        # Strip them and ignore empty lines
        added_options = add_options(poll, text)

        if len(added_options) == 0:
            return "❌ No new options have been added."

        next_option(chat, poll, added_options)

    # Get the amount of possible votes per user for this poll
    elif expected_input == ExpectedInput.vote_count:
        if poll.vote_type == VoteType.limited_vote.name:
            error_message = f"Please send me a number between 1 and {len(poll.options)}"
        elif poll.vote_type == VoteType.cumulative_vote.name:
            error_message = "Please send me a number bigger than 0"

        try:
            amount = int(text)
        except BaseException:
            return error_message

        # Check for valid count
        if amount < 1 or (poll.vote_type == VoteType.limited_vote.name and amount > len(poll.options)):
            return error_message

        poll.number_of_votes = amount

        create_poll(session, poll, user, chat)

    # Add new options after poll creation
    elif expected_input == ExpectedInput.new_option:
        added_options = add_options(poll, text)

        if len(added_options) > 0:
            text = 'Options have been added:\n'
            for option in added_options:
                text += f'\n*{option}*'
            chat.send_message(text, parse_mode='markdown')
        else:
            chat.send_message('No new option has been added')

        # Reset expected input
        poll.expected_input = None

        text = get_settings_text(poll)
        keyboard = get_settings_keyboard(poll)
        message = chat.send_message(
            text,
            parse_mode='markdown',
            reply_markup=keyboard,
        )

        # Delete old references
        session.query(Reference) \
            .filter(Reference.poll == poll) \
            .filter(Reference.admin_chat_id == chat.id) \
            .delete()

        # Create new reference
        reference = Reference(
            poll,
            admin_chat_id=chat.id,
            admin_message_id=message.message_id
        )
        session.add(reference)
        session.commit()

        update_poll_messages(session, bot, poll)
