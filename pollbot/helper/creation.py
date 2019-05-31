"""Poll creation helper."""
from pollbot.helper.enums import VoteTypeTranslation, ExpectedInput
from pollbot.helper.display import get_poll_management_text
from pollbot.telegram.keyboard import (
    get_options_entered_keyboard,
    get_management_keyboard,
)
from pollbot.models import Reference


def get_vote_type_help_text(poll):
    """Create the help text for vote types."""
    vote_type = VoteTypeTranslation[poll.vote_type]
    return f"""Current vote type: *{vote_type}*

*Single vote*:
Every user gets a single vote.

*Block vote*:
Every user is allowed to vote each option without restrictions (But only one vote per option).

*Limited vote*:
Every user gets a fixed number of votes they can distribute (But only one vote per option).

*Cumulative vote*:
Every user gets a fixed number of votes they can distribute as they will.
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
