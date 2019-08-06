"""Get the text describing the current state of the poll."""
import math
import string
from datetime import date
from sqlalchemy import func

from pollbot.i18n import i18n
from pollbot.helper.enums import PollType
from pollbot.helper import (
    poll_has_limited_votes,
    poll_allows_cumulative_votes,
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


def get_poll_text(session, poll, show_warning, management=False):
    """Create the text of the poll."""
    total_user_count = session.query(User.id) \
        .join(Vote) \
        .join(PollOption) \
        .filter(PollOption.poll == poll) \
        .group_by(User.id) \
        .count()

    # Name and description
    lines = []
    lines.append(f'✉️ *{poll.name}*')
    if poll.description is not None:
        lines.append(f'_{poll.description}_')

    # Anonymity information
    if not poll.results_visible and not poll.should_show_result() or \
            poll.anonymous and not poll.closed:
        lines.append('')
    if poll.anonymous and not poll.closed:
        lines.append(f"_{i18n.t('poll.anonymous', locale=poll.locale)}_")
    if not poll.results_visible and not poll.should_show_result():
        lines.append(f"_{i18n.t('poll.results_not_visible', locale=poll.locale)}_")

    # Sort the options accordingly to the polls settings
    options = get_sorted_options(poll, total_user_count)

    # All options with their respective people percentage
    for index, option in enumerate(options):
        lines.append('')
        lines.append(get_option_line(session, option, index))
        if option.description is not None:
            lines.append(f'┆ _{option.description}_')

        if poll.should_show_result() and poll.show_percentage:
            lines.append(get_percentage_line(option, total_user_count))

        # Add the names of the voters to the respective options
        if poll.should_show_result() and not poll.anonymous and len(option.votes) > 0:
            # Sort the votes accordingly to the poll's settings
            votes = get_sorted_votes(poll, option.votes)
            for index, vote in enumerate(votes):
                vote_line = get_vote_line(poll, option, vote, index)
                lines.append(vote_line)
    lines.append('')

    if poll_has_limited_votes(poll):
        lines.append(i18n.t('poll.vote_times',
                            locale=poll.locale,
                            amount=poll.number_of_votes))

    # Total user count information
    information_line = get_vote_information_line(poll, total_user_count)
    if information_line is not None:
        lines.append(information_line)

    if not poll.anonymous:
        remaining_votes = get_remaining_votes(session, poll)
        lines += remaining_votes

    if poll.due_date is not None:
        lines.append(i18n.t('poll.due',
                            locale=poll.locale,
                            date=poll.get_formatted_due_date()))

    # Own poll note
    if not management:
        lines.append(i18n.t('poll.own_poll', locale=poll.locale))

    # Notify users that poll is closed
    if poll.closed and not management:
        lines.append(i18n.t('poll.closed', locale=poll.locale))

    if show_warning and not management:
        lines.append(i18n.t('poll.too_many_votes', locale=poll.locale))

    return '\n'.join(lines)


def get_option_line(session, option, index):
    """Get the line with vote count for this option."""
    # Special formating for polls with european date format
    if option.is_date and option.poll.european_date_format:
        option_date = date.fromisoformat(option.name)
        option_name = option_date.strftime('%d.%m.%Y (%A)')
    elif option.is_date:
        option_date = date.fromisoformat(option.name)
        option_name = option_date.strftime('%Y-%m-%d (%A)')
    else:
        option_name = option.name

    prefix = ''
    if option.poll.poll_type == PollType.doodle.name:
        letters = string.ascii_letters
        prefix = f'{letters[index]}) '

    if len(option.votes) > 0 and option.poll.should_show_result():
        if poll_allows_cumulative_votes(option.poll):
            vote_count = sum([vote.vote_count for vote in option.votes])
        else:
            vote_count = len(option.votes)
        return f'┌ {prefix}*{option_name}* ({vote_count} votes)'
    else:
        return f'┌ {prefix}*{option_name}*'


def get_vote_line(poll, option, vote, index):
    """Get the line showing an actual vote."""
    user_mention = f'[{vote.user.name}](tg://user?id={vote.user.id})'
    if index == (len(option.votes) - 1):
        vote_line = f'└ {user_mention}'
    else:
        vote_line = f'├ {user_mention}'

    if poll_allows_cumulative_votes(poll):
        vote_line += f' ({vote.vote_count} votes)'
    elif poll.poll_type == PollType.doodle.name:
        vote_line += f' ({vote.type})'

    return vote_line


def get_percentage_line(option, total_user_count):
    """Get the percentage line for each option."""
    percentage = calculate_percentage(option, total_user_count)
    filled_slots = math.floor(percentage/10)

    if len(option.votes) == 0 or option.poll.anonymous:
        line = '└ '
    else:
        line = '│ '

    line += filled_slots * '▬'
    line += (10-filled_slots) * '▭'
    line += f' ({percentage:.0f}%)'

    return ''.join(line)


def get_vote_information_line(poll, total_user_count):
    """Get line that shows information about total user votes."""
    vote_information = None
    if total_user_count > 1:
        vote_information = i18n.t('poll.many_users_voted',
                                  locale=poll.locale,
                                  count=total_user_count)
    elif total_user_count == 1:
        vote_information = i18n.t('poll.one_user_voted', locale=poll.locale)

    if vote_information is not None and poll_allows_multiple_votes(poll):
        total_count = calculate_total_votes(poll)
        vote_information += i18n.t('poll.total_votes', locale=poll.locale, count=total_count)

    return vote_information


def get_remaining_votes(session, poll):
    """Get the remaining votes for a poll."""
    if not poll_has_limited_votes(poll)  \
       or not poll.should_show_result() \
       or poll.anonymous:
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
    lines.append(i18n.t('poll.remaining_votes', locale=poll.locale))
    for user_votes in remaining_user_votes:
        lines.append(i18n.t('poll.remaining_votes_user',
                            locale=poll.locale,
                            name=user_votes[0],
                            count=poll.number_of_votes - user_votes[1]))

    return lines
