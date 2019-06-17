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
    get_skip_description_keyboard,
)

from pollbot.models import Reference


@session_wrapper()
def handle_private_text(bot, update, session, user):
    """Read all private messages and the creation of polls."""
    text = update.message.text.strip()
    poll = user.current_poll
    chat = update.message.chat

    # The user is currently not expecting input or no poll is set
    if user.current_poll is None or user.expected_input is None:
        return
    else:
        expected_input = ExpectedInput[user.expected_input]
        actions = {
            ExpectedInput.name: handle_set_name,
            ExpectedInput.description: handle_set_description,
            ExpectedInput.options: handle_create_options,
            ExpectedInput.vote_count: handle_set_vote_count,
            ExpectedInput.new_option: handle_new_option,
            ExpectedInput.new_user_option: handle_user_option_addition,
        }

        actions[expected_input](bot, update, session, user, text, poll, chat)


def handle_set_name(bot, update, session, user, text, poll, chat):
    """Set the name of the poll."""
    poll.name = text
    user.expected_input = ExpectedInput.description.name
    keyboard = get_skip_description_keyboard(poll)
    chat.send_message(
        'Now send me the description.',
        reply_markup=keyboard,
    )


def handle_set_description(bot, update, session, user, text, poll, chat):
    """Set the description of the poll."""
    poll.description = text
    user.expected_input = ExpectedInput.options.name
    message = 'Now send me the first option (Or send multiple options at once, each option on a new line)'
    chat.send_message(message, reply_markup=get_open_datepicker_keyboard(poll))


def handle_create_options(bot, update, session, user, text, poll, chat):
    """Add options to the poll."""
    # Multiple options can be sent at once separated by newline
    # Strip them and ignore empty lines
    added_options = add_options(poll, text)

    if len(added_options) == 0:
        return "❌ No new options have been added."

    next_option(chat, poll, added_options)


def handle_set_vote_count(bot, update, session, user, text, poll, chat):
    """Set the amount of possible votes for this poll."""
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


def handle_new_option(bot, update, session, user, text, poll, chat):
    """Add a new option after poll creation."""
    added_options = add_options(poll, text)

    if len(added_options) > 0:
        text = 'Options have been added:\n'
        for option in added_options:
            text += f'\n*{option}*'
        chat.send_message(text, parse_mode='markdown')
    else:
        chat.send_message('No new option has been added')

    # Reset expected input
    user.current_poll = None
    user.expected_input = None

    text = get_settings_text(poll)
    keyboard = get_settings_keyboard(poll)
    message = chat.send_message(
        text,
        parse_mode='markdown',
        reply_markup=keyboard,
    )

    # Delete old references
    references = session.query(Reference) \
        .filter(Reference.poll == poll) \
        .filter(Reference.admin_chat_id == chat.id) \
        .all()
    for reference in references:
        try:
            bot.delete_message(chat.id, reference.admin_message_id)
        except:
            pass
        session.delete(reference)

    # Create new reference
    reference = Reference(
        poll,
        admin_chat_id=chat.id,
        admin_message_id=message.message_id
    )
    session.add(reference)
    session.commit()

    update_poll_messages(session, bot, poll)


def handle_user_option_addition(bot, update, session, user, text, poll, chat):
    """Handle the addition of options from and arbitrary user."""
    if not poll.allow_new_options:
        user.current_poll = None
        user.expected_input = None
        chat.send_message('You are no longer allowed to add new options.')

    added_options = add_options(poll, text)

    if len(added_options) > 0:
        # Reset user
        user.current_poll = None
        user.expected_input = None

        # Send message
        text = 'Options have been added:\n'
        for option in added_options:
            text += f'\n*{option}*'
        chat.send_message(text, parse_mode='markdown')

        # Upate all polls
        update_poll_messages(session, bot, poll)
    else:
        chat.send_message('No new option has been added')
