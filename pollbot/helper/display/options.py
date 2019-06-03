"""The settings management text."""
from pollbot.helper.enums import (
    VoteTypeTranslation,
    SortOptionTranslation,
)


def get_options_text(poll):
    """Compile the options text for this poll."""
    text = f"""*General settings:*
Vote type: {VoteTypeTranslation[poll.vote_type]}
Anonymity: {'Names are not visible' if poll.anonymous else 'Names are visible'}
*Visible results*: {'Results are not visible until poll is closed' if poll.results_visible else 'Results are directly visible'}

*Sorting:*
"""

    # Sorting of user names
    if not poll.anonymous:
        text += f"User: {SortOptionTranslation[poll.user_sorting]}\n"

    text += f'Option: {SortOptionTranslation[poll.option_sorting]}'

    return text
