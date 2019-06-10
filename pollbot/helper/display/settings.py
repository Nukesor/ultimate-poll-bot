"""The settings management text."""
from pollbot.helper.enums import (
    VoteTypeTranslation,
    SortOptionTranslation,
)


def get_settings_text(poll):
    """Compile the options text for this poll."""
    text = []
    text.append(f"*Vote type*: {VoteTypeTranslation[poll.vote_type]}")

    if poll.anonymous:
        text.append("*Anonymity*: Names are not visible")
    else:
        text.append("*Anonymity*: Names are visible")

    if poll.results_visible:
        text.append("*Visible results*: Results are directly visible")
    else:
        text.append("*Visible results*: Results are not visible until poll is closed")

    text.append('')

    if poll.results_visible:
        if poll.show_percentage:
            text.append("*Percentage*: Visible")
        else:
            text.append("*Percentage*: Hidden")

    text.append('')

    # Sorting of user names
    if not poll.anonymous:
        text.append(f'*User Sorting*: {SortOptionTranslation[poll.user_sorting]}')

    text.append(f'*Option Sorting*: {SortOptionTranslation[poll.option_sorting]}')

    return '\n'.join(text)
