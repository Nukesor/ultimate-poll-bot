"""Poll creation helper."""
from pollbot.helper.enums import ExpectedInput
from pollbot.helper.display import get_poll_management_text
from pollbot.telegram.keyboard import (
    get_options_entered_keyboard,
    get_management_keyboard,
)
from pollbot.models import PollOption, Reference


def next_option(tg_chat, poll, options):
    """Send the options message during the creation ."""
    poll.expected_input = ExpectedInput.options.name
    keyboard = get_options_entered_keyboard(poll)

    if len(options) == 1:
        text = f"*{options[0]}* has been added. 👍\nSend the *another option* or click *done*."
    else:
        text = 'Options have been added:\n'
        for option in options:
            text += f'\n*{option}*'
        text += '\n\nSend the next option or click *done*.'

    tg_chat.send_message(text, reply_markup=keyboard, parse_mode='Markdown')


def create_poll(session, poll, user, chat, message=None):
    """Finish the poll creation."""
    poll.created = True
    poll.expected_input = None
    user.current_poll = None

    if message:
        message = message.edit_text(
            get_poll_management_text(session, poll),
            parse_mode='markdown',
            reply_markup=get_management_keyboard(poll)
        )
    else:
        message = chat.send_message(
            get_poll_management_text(session, poll),
            parse_mode='markdown',
            reply_markup=get_management_keyboard(poll)
        )

    reference = Reference(
        poll,
        admin_chat_id=chat.id,
        admin_message_id=message.message_id
    )
    session.add(reference)
    session.commit()


def add_options(poll, text):
    """Add a new option to the poll."""
    options_to_add = [x.strip() for x in text.split('\n') if x.strip() != '']
    added_options = []

    for option_to_add in options_to_add:
        if option_is_duplicate(poll, option_to_add) or option_to_add in added_options:
            continue

        poll_option = PollOption(poll, option_to_add)
        poll.options.append(poll_option)

        added_options.append(option_to_add)

    return added_options


def option_is_duplicate(poll, option_to_add):
    """Check whether this option already exists on this poll."""
    for existing_option in poll.options:
        if existing_option.name == option_to_add:
            return True

    return False
