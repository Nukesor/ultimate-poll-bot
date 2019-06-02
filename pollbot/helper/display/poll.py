"""Get the text describing the current state of the poll."""
import math
from sqlalchemy import func
from pollbot.helper.enums import VoteType
from pollbot.helper import (
    poll_has_limited_votes,
    poll_is_cumulative,
    poll_allows_multiple_votes,
    calculate_total_votes,
)
from pollbot.models import (
    User,
    PollOption,
    Vote,
)
from pollbot.helper.display import (
    get_sorted_options,
    get_sorted_votes,
    calculate_percentage,
)


def get_poll_text(session, poll):
    """Create the text of the poll."""
    lines = [f"{poll.name}"]
    lines.append(f'{poll.description}')

    total_user_count = session.query(User.id) \
        .join(Vote) \
        .join(PollOption) \
        .filter(PollOption.poll == poll) \
        .group_by(User.id) \
        .count()

    # Name and description
    lines = []
    lines.append(f'*{poll.name}*')
    lines.append(f'_{poll.description}_')

    # Sort the options accordingly to the polls settings
    options = get_sorted_options(poll, poll.options.copy(), total_user_count)

    # All options with their respective people percentage
    for option in options:
        lines.append('')
        lines.append(get_option_line(session, option))

        lines.append(get_percentage_line(option, total_user_count))

        # Add the names of the voters to the respective options
        if not poll.anonymous and len(option.votes) > 0:
            # Sort the votes accordingly to the poll's settings
            votes = get_sorted_votes(poll, option.votes)
            for index, vote in enumerate(votes):
                vote_line = get_vote_line(poll, option, vote, index)
                lines.append(vote_line)

    if poll_has_limited_votes(poll):
        lines.append(f'\nEvery user can vote *{poll.number_of_votes} times*')

    # Total user count information
    information_line = get_vote_information_line(poll, total_user_count)
    if information_line is not None:
        lines.append(information_line)

    if not poll.anonymous:
        remaining_votes = get_remaining_votes(session, poll)
        lines += remaining_votes

    # Notify users that poll is closed
    if poll.closed:
        lines.insert(0, '⚠️ *This poll is closed* ⚠️\n')
        lines.append('\n⚠️ *This poll is closed* ⚠️')

    return '\n'.join(lines)


def get_option_line(session, option):
    """Get the line with vote count for this option."""
    if len(option.votes) > 0:
        if poll_is_cumulative(option.poll):
            vote_count = sum([vote.vote_count for vote in option.votes])
        else:
            vote_count = len(option.votes)
        return f'*{option.name}* ({vote_count} votes)'
    else:
        return f'*{option.name}*'


def get_vote_line(poll, option, vote, index):
    """Get the line showing an actual vote."""
    if index != len(poll.votes) - 1:
        vote_line = f'├ {vote.user.name}'
    else:
        vote_line = f'└ {vote.user.name}'

    if poll_is_cumulative(option.poll):
        vote_line += f' ({vote.vote_count} votes)'

    return vote_line


def get_percentage_line(option, total_user_count):
    """Get the percentage line for each option."""
    percentage = calculate_percentage(option, total_user_count)
    filled_slots = math.floor(percentage/10)

    line = '│ '
    line += filled_slots * '●'
    line += (10-filled_slots) * '○'
    line += f' ({percentage}%)'

    return ''.join(line)


def get_vote_information_line(poll, total_user_count):
    """Get line that shows information about total user votes."""
    vote_information = None
    if total_user_count > 1:
        vote_information = f'*{total_user_count} users* voted so far'
    elif total_user_count == 1:
        vote_information = '*One user* voted so far'

    if vote_information is not None and poll_allows_multiple_votes(poll):
        total_count = calculate_total_votes(poll)
        vote_information += f' ({total_count} votes)'

    return vote_information


def get_remaining_votes(session, poll):
    """Get the remaining votes for a poll."""
    if not poll_has_limited_votes(poll):
        return []

    user_vote_count = func.sum(Vote.vote_count).label('user_vote_count')
    remaining_user_votes = session.query(User.name, user_vote_count) \
        .join(Vote) \
        .filter(Vote.poll == poll) \
        .group_by(User.name) \
        .having(user_vote_count < poll.number_of_votes) \
        .order_by(User.name) \
        .all()

    if len(remaining_user_votes) == 0:
        return []

    lines = []
    lines.append('\nRemaining votes:')
    for user_votes in remaining_user_votes:
        lines.append(f'{user_votes[0]}: {poll.number_of_votes - user_votes[1]} votes')

    return lines
