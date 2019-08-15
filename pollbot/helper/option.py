from pollbot.helper import poll_allows_cumulative_votes
from pollbot.helper.enums import (
    VoteResultType,
    OptionSorting,
    PollType,
)


def get_sorted_options(poll, total_user_count=0):
    """Sort the options depending on the poll's current settings."""
    options = poll.options.copy()

    def get_option_name(option):
        """Get the name of the option."""
        return option.name

    def get_option_percentage(option):
        """Get the name of the option."""
        return calculate_percentage(option, total_user_count)

    if poll.option_sorting == OptionSorting.option_name.name:
        options.sort(key=get_option_name)

    elif poll.option_sorting == OptionSorting.option_percentage.name:
        options.sort(key=get_option_percentage, reverse=True)

    return options


def calculate_percentage(option, total_user_count):
    """Calculate the percentage for this option."""
    # Return 0 if:
    # - No user voted yet
    # - This option has no votes
    # - The poll has no votes
    if total_user_count == 0:
        return 0
    if len(option.votes) == 0:
        return 0

    poll_vote_count = sum([vote.vote_count for vote in option.poll.votes])
    if poll_vote_count == 0:
        return 0

    if poll_allows_cumulative_votes(option.poll):
        option_vote_count = sum([vote.vote_count for vote in option.votes])

        percentage = round(option_vote_count/poll_vote_count * 100)

    elif option.poll.poll_type == PollType.doodle.name:
        score = 0
        for vote in option.votes:
            if vote.type == VoteResultType.yes.name:
                score += 1
            elif vote.type == VoteResultType.maybe.name:
                score += 0.5

        return score/total_user_count * 100
    else:
        percentage = round(len(option.votes)/total_user_count * 100)

    return percentage
