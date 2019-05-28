"""Poll creation helper."""
import math
from telegram.error import BadRequest

from pollbot.helper.keyboard import get_vote_keyboard
from pollbot.models import (
    User,
    PollOption,
    Vote,
)


def update_poll(session, bot, poll):
    """Update all messages (references) of a poll."""
    for reference in poll.references:
        try:
            # Admin poll management interface
            if reference.inline_message_id is None:
                keyboard = get_vote_keyboard(poll)
                text = get_poll_management_text(session, poll)
                bot.edit_message_text(
                    text,
                    chat_id=reference.admin_chat_id,
                    message_id=reference.admin_message_id,
                    reply_markup=keyboard,
                    parse_mode='markdown',
                )

            # Edit message via inline_message_id
            else:
                # Create text and keyboard
                text = get_poll_text(session, poll)
                keyboard = get_vote_keyboard(poll)

                bot.edit_message_text(
                    text,
                    inline_message_id=reference.inline_message_id,
                    reply_markup=keyboard,
                    parse_mode='markdown',
                )
        except BadRequest as e:
            if e.message.startswith('Message_id_invalid'):
                session.delete(reference)
                session.commit()
            else:
                raise


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


def get_poll_management_text(session, poll):
    """Create the management interface for a poll."""
    poll_text = get_poll_text(session, poll)

    management_text = 'Manage your poll:\n\n'
    management_text += poll_text

    return management_text
