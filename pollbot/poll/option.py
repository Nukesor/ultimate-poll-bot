from typing import List

from pollbot.poll.helper import poll_allows_cumulative_votes
from pollbot.enums import (
    VoteResultType,
    OptionSorting,
    PollType,
)


def add_text_options_from_list(session, poll, options: List[str]):
    """Add multiple new options to the poll."""
    options_to_add = map(str.strip, options)
    added_options = []

    for option_to_add in options_to_add:
        option = add_option(poll, option_to_add, added_options, False)
        if option is None:
            continue

        session.add(option)
        session.commit()

        added_options.append(option_to_add)

    return added_options


def add_options_multiline(session, poll, text, is_date=False):
    """Add one or multiple new options to the poll."""
    options_to_add = [x.strip() for x in text.split("\n") if x.strip() != ""]
    added_options = []

    for option_to_add in options_to_add:
        option = add_option(poll, option_to_add, added_options, is_date)
        if option is None:
            continue

        session.add(option)
        session.commit()

        added_options.append(option_to_add)

    return added_options


def add_option(poll, text, added_options, is_date):
    """Parse the incoming text and create a single option from it."""
    description = None
    description_descriminator = None
    if "--" in text:
        description_descriminator = "--"
    elif "—" in text:
        description_descriminator = "—"
    # Extract the description if existing

    if description_descriminator is not None:
        # Extract and strip the description
        splitted = text.split(description_descriminator, 1)
        text = splitted[0].strip()
        description = splitted[1].strip()
        if description == "":
            description = None

    if option_is_duplicate(poll, text) or text in added_options:
        return None

    option = Option(poll, text)
    option.description = description
    option.is_date = is_date
    poll.options.append(option)

    return option


def next_option(tg_chat, poll, options):
    """Send the options message during the creation ."""
    locale = poll.user.locale
    poll.user.expected_input = ExpectedInput.options.name
    keyboard = get_options_entered_keyboard(poll)

    if len(options) == 1:
        text = i18n.t("creation.option.single_added", locale=locale, option=options[0])
    else:
        text = i18n.t("creation.option.multiple_added", locale=locale)
        for option in options:
            text += f"\n*{option}*"
        text += "\n\n" + i18n.t("creation.option.next", locale=locale)

    if len(text) > 3800:
        error_message = i18n.t("misc.over_4000", locale=locale)
        raise RollbackException(error_message)

    tg_chat.send_message(text, reply_markup=keyboard, parse_mode="Markdown")


def get_sorted_options(poll, total_user_count=0):
    """Sort the options depending on the poll's current settings."""
    options = poll.options.copy()

    def get_option_percentage(option):
        """Get the name of the option."""
        return calculate_percentage(option, total_user_count)

    if poll.option_sorting == OptionSorting.percentage.name:
        options.sort(key=get_option_percentage, reverse=True)

    return options


def calculate_percentage(option, total_user_count):
    """Calculate the percentage for this option."""
    # Return 0 if:
    # - No voted on this poll yet
    # - This option has no votes
    if total_user_count == 0:
        return 0
    if len(option.votes) == 0:
        return 0

    poll_vote_count = sum([vote.vote_count for vote in option.poll.votes])
    if poll_vote_count == 0:
        return 0

    if poll_allows_cumulative_votes(option.poll):
        option_vote_count = sum([vote.vote_count for vote in option.votes])

        percentage = round(option_vote_count / poll_vote_count * 100)

    elif option.poll.poll_type == PollType.doodle.name:
        score = 0
        for vote in option.votes:
            if vote.type == VoteResultType.yes.name:
                score += 1
            elif vote.type == VoteResultType.maybe.name:
                score += 0.5

        return score / total_user_count * 100
    else:
        percentage = len(option.votes) / total_user_count * 100

    return percentage


def option_is_duplicate(poll, option_to_add):
    """Check whether this option already exists on this poll."""
    for existing_option in poll.options:
        if existing_option.name == option_to_add:
            return True

    return False
