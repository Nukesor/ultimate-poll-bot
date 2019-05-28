"""Poll creation helper."""
import math

from pollbot.models import (
    User,
    PollOption,
    Vote,
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

    lines = []
    lines.append(f'*{poll.name}*')
    lines.append(f'_{poll.description}_')
    for poll_option in poll.options:
        lines.append('')
        lines.append(f'*{poll_option.name}*')
        lines.append(calculate_percentage_line(poll_option, total_user_count))

        if not poll.anonymous:
            for index, vote in enumerate(poll_option.votes):
                if index != len(poll.options) - 1:
                    line = f'├ {vote.user.name}'
                else:
                    line = f'└ {vote.user.name}'

                lines.append(line)

    lines.append(f'\n{total_user_count} users voted so far')

    return '\n'.join(lines)


def calculate_percentage_line(poll_option, total_user_count):
    """Calculate the percentage line for each option."""
    if total_user_count == 0:
        percentage = 0
    else:
        percentage = round(len(poll_option.votes)/total_user_count * 100)
    filled_slots = math.floor(percentage/10)

    line = '| '
    line += filled_slots * '●'
    line += (10-filled_slots) * '○'
    line += f' ({percentage}%)'

    return ''.join(line)
