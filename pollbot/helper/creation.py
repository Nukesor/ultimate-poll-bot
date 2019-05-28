"""Poll creation helper."""

from pollbot.helper.enums import poll_type_translation, PollCreationStep
from pollbot.helper.keyboard import get_options_entered_keyboard


def get_init_text(poll):
    """Compile the poll creation initialization text."""
    message = f"""Only a few steps left:

Current settings are:
Poll type: {poll_type_translation[poll.type]}
Anonymity: {'Anonymous' if poll.anonymous else 'Names are visible'}

Send me the name of the poll or configure the poll with the buttons below.
"""
    return message


def init_description(tg_chat, poll):
    """Send the description message during poll creation."""
    poll.creation_step = PollCreationStep.description.name
    tg_chat.send_message('Please send me a description for this poll')


def init_options(tg_chat, poll):
    """Send the options message during the creation step."""
    poll.creation_step = PollCreationStep.options.name
    tg_chat.send_message('Please send me a message for each possible choice in your poll')


def next_option(tg_chat, poll, option):
    """Send the options message during the creation step."""
    poll.creation_step = PollCreationStep.options.name
    keyboard = get_options_entered_keyboard(poll)
    tg_chat.send_message(f"*{option}* has been added.", reply_markup=keyboard, parse_mode='Markdown')
