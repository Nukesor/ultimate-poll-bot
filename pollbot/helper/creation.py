"""Poll creation helper."""

from pollbot.helper.enums import VoteTypeTranslation, ExpectedInput
from pollbot.telegram.keyboard import get_options_entered_keyboard


def get_vote_type_help_text(poll):
    """Create the help text for vote types."""
    vote_type = VoteTypeTranslation[poll.vote_type]
    return f"""Current vote type: *{vote_type}*

*Single vote*:
Every user gets a single vote.

*Multiple votes*:
Every user is allowed to vote each option without restrictions (But only one vote per option).
"""


def get_init_text(poll):
    """Compile the poll creation initialization text."""
    message = f"""Hey there!
You are about to create a new poll 👌

The current settings for the poll are:

*Vote type*: {VoteTypeTranslation[poll.vote_type]}
*Anonymity*: {'Names are not visible' if poll.anonymous else 'Names are visible'}

Please follow these steps:
1. Configure the poll to your needs 🙂
2. 👇 Send me the name of this poll. 👇
"""
    return message


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
