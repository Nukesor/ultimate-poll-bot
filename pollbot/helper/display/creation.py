"""Text helper for poll creation."""
from pollbot.helper.enums import VoteTypeTranslation


def get_vote_type_help_text(poll):
    """Create the help text for vote types."""
    vote_type = VoteTypeTranslation[poll.vote_type]
    return f"""Current vote type: *{vote_type}*

*Single vote*:
Every user gets a single vote.

*Block vote*:
Every user can vote for all (or less) options.

*Limited vote*:
Every user gets a fixed number of votes they can distribute, but only once per option.

*Cumulative vote*:
Every user gets a fixed number of votes they can distribute as they like (even multiple votes per option).
"""


def get_init_text(poll):
    """Compile the poll creation initialization text."""
    message = f"""Hey there!
You are about to create a new poll 👌

The current settings for the poll are:

*Vote type*: {VoteTypeTranslation[poll.vote_type]}
*Anonymity*: {'Names are not visible' if poll.anonymous else 'Names are visible'}
*Visible results*: {'Results are directly visible' if poll.results_visible else 'Results are not visible until poll is closed'}

Please follow these steps:
1. Configure the poll to your needs 🙂
2. 👇 Send me the name of this poll. 👇
"""
    return message


def get_datepicker_text(poll):
    """Get the text for the datepicker."""
    text = """*Datepicker:*
To add date, select it and click _Pick this date_.

*Current options:*"""
    for option in poll.options:
        text += f'\n{option.name}'

    return text
