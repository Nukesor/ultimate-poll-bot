from typing import Any, List, Optional, Union

from sqlalchemy.orm.scoping import scoped_session

from pollbot.enums import OptionSorting, PollType, VoteResultType
from pollbot.models import Option, Poll
from pollbot.poll.helper import poll_allows_cumulative_votes
from pollbot.poll.vote import init_votes_for_new_options


def add_single_option(
    session: scoped_session, poll: Poll, line: str, is_date: bool
) -> None:
    """Add a single option from a single line."""
    option = add_option(poll, line, [], is_date)

    if option is None:
        return

    session.add(option)
    session.flush()

    # Initialize priority votes for new option
    init_votes_for_new_options(session, poll, [option.name])


def add_options_multiline(
    session: scoped_session, poll: Poll, text: str, is_date: bool = False
) -> List[Union[Any, str]]:
    """Add one or multiple new options to the poll from a block of text."""
    options_to_add = [x.strip() for x in text.split("\n") if x.strip() != ""]
    return add_multiple_options(session, poll, options_to_add, is_date=is_date)


def add_multiple_options(
    session: scoped_session,
    poll: Poll,
    options_to_add: List[str],
    is_date: bool = False,
) -> List[Union[Any, str]]:
    """Create options from a list of strings."""
    added_options = []

    for option_to_add in options_to_add:
        option = add_option(poll, option_to_add, added_options, is_date)
        if option is None:
            continue

        session.add(option)
        session.flush()

    # Initialize priority votes for new options
    if len(added_options) > 0:
        init_votes_for_new_options(session, poll, added_options)

    return added_options


def add_option(
    poll: Poll, text: str, added_options: List[str], is_date: bool
) -> Optional[Option]:
    """Parse the incoming text and create a single option from it.

    We allow option descriptions after an `--` or `—` delimiter.
    `added_options` is a list of names of options that have already
       been added during this single request.
    """
    description = None

    # Check if there's a description delimiter in the line
    description_descriminator = None
    if "--" in text:
        description_descriminator = "--"
    elif "—" in text:
        description_descriminator = "—"

    # Extract the description if existing
    if description_descriminator is not None:
        splitted = text.split(description_descriminator, 1)
        text = splitted[0].strip()
        description = splitted[1].strip()
        if description == "":
            description = None

    # Early return, if this option already exists, or
    # if we already added this option in this request
    if option_is_duplicate(poll, text) or text in added_options:
        return None

    option = Option(poll, text)
    option.description = description
    option.is_date = is_date

    added_options.append(text)

    return option


def get_sorted_options(
    poll: Poll, total_user_count: int = 0
) -> List[Union[Option, Any]]:
    """Sort the options depending on the poll's current settings."""
    options = poll.options.copy()

    def get_option_percentage(option):
        """Get the name of the option."""
        return calculate_percentage(option, total_user_count)

    if poll.option_sorting == OptionSorting.percentage.name:
        options.sort(key=get_option_percentage, reverse=True)

    return options


def calculate_percentage(option: Option, total_user_count: int) -> Union[float, int]:
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


def option_is_duplicate(poll: Poll, option_to_add: str) -> bool:
    """Check whether this option already exists on this poll."""
    for existing_option in poll.options:
        if existing_option.name == option_to_add:
            return True

    return False
