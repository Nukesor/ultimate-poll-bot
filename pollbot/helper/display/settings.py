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

    if poll.allow_new_options:
        text.append("*Custom user options*: Anyone can add new options")
    else:
        text.append("*Custom user options*: Only you can add new options")

    if poll.results_visible:
        if poll.show_percentage:
            text.append("*Percentage*: Visible")
        else:
            text.append("*Percentage*: Hidden")

    if poll.has_date_option():
        if poll.european_date_format:
            text.append("*Date format*: DD.MM.YYYY")
        else:
            text.append("*Date format*: YYYY-MM-DD")

    text.append('')

    # Sorting of user names
    if not poll.anonymous:
        text.append(f'*User Sorting*: {SortOptionTranslation[poll.user_sorting]}')

    text.append(f'*Option Sorting*: {SortOptionTranslation[poll.option_sorting]}')

    return '\n'.join(text)
