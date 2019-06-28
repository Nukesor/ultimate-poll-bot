"""Text helper for poll creation."""
from datetime import date
from pollbot.helper.enums import VoteTypeTranslation


def get_vote_type_help_text(poll):
    """Create the help text for vote types."""
    vote_type = VoteTypeTranslation[poll.vote_type]
    return f"""Current poll type: *{vote_type}*

*Single vote*:
Every user gets a single vote. The default and normal voting mode.

*Block vote*:
Every user can vote for all (or less) options. Useful for finding the most wanted options in a group, e.g. games that should be played on a LAN-Party.

*Limited vote*:
Every user gets a fixed number of votes they can distribute, but only once per option.
Pretty much like block vote, but people need to prioritize.
This mode is good for limiting the amount of possible winners e.g. if you only want max 4 games on your LAN-Party.

*Cumulative vote*:
Every user gets a fixed number of votes they can distribute as they like (even multiple votes per option).
This mode has a little more depth than limited vote, since it allows users to vote on a single option multiple times.

*Unlimited votes* (or the shopping list):
Every user can vote as often on any option as they want.
This is great if you want to, for instance, determine how much stuff everyone wants for the next festival trip.
"""


def get_init_text(poll):
    """Compile the poll creation initialization text."""
    message = f"""Hey there!
You are about to create a new poll 👌

The current settings for this poll are:

*Poll type*: {VoteTypeTranslation[poll.vote_type]}
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
        if option.is_date and option.poll.european_date_format:
            option_date = date.fromisoformat(option.name)
            option_name = option_date.strftime('%d.%m.%Y')
            text += f'\n{option_name}'
        else:
            text += f'\n{option.name}'

    return text
