from sqlalchemy import func

from pollbot.i18n import i18n
from pollbot.helper import (
    poll_allows_cumulative_votes,
    poll_allows_multiple_votes,
    calculate_total_votes,
)
from pollbot.helper.enums import (
    UserSorting,
    PollType,
)
from pollbot.models import (
    User,
    PollOption,
    Vote,
)


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


def get_vote_information_line(poll, context):
    """Get line that shows information about total user votes."""
    vote_information = None
    if context.total_user_count > 1:
        vote_information = i18n.t('poll.many_users_voted',
                                  locale=poll.locale,
                                  count=context.total_user_count)
    elif context.total_user_count == 1:
        vote_information = i18n.t('poll.one_user_voted', locale=poll.locale)

    if vote_information is not None and poll_allows_multiple_votes(poll):
        total_count = calculate_total_votes(poll)
        vote_information += i18n.t('poll.total_votes',
                                   locale=poll.locale,
                                   count=total_count)

    return vote_information


def get_remaining_votes_lines(session, poll):
    """Get the remaining votes for a poll."""
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
