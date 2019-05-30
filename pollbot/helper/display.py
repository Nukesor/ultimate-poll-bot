"""Poll creation helper."""
import math
from telegram.error import BadRequest

from pollbot.helper.enums import ExpectedInput, VoteTypeTranslation
from pollbot.telegram.keyboard import get_vote_keyboard, get_management_keyboard
from pollbot.models import (
    User,
    PollOption,
    Vote,
)


def update_poll_messages(session, bot, poll):
    """Update all messages (references) of a poll."""
    for reference in poll.references:
        try:
            # Admin poll management interface
            if reference.inline_message_id is None:
                if poll.expected_input == ExpectedInput.votes.name:
                    keyboard = get_vote_keyboard(poll, show_back=True)
                else:
                    keyboard = get_management_keyboard(poll)
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


def remove_poll_messages(session, bot, poll):
    """Remove all messages (references) of a poll."""
    for reference in poll.references:
        try:
            # Admin poll management interface
            if reference.inline_message_id is None:
                bot.edit_message_text(
                    'This poll has been permanently deleted.',
                    chat_id=reference.admin_chat_id,
                    message_id=reference.admin_message_id,
                )

            # Edit message via inline_message_id
            else:
                # Create text and keyboard
                bot.edit_message_text(
                    'This poll has been permanently deleted.',
                    inline_message_id=reference.inline_message_id,
                )
        except BadRequest as e:
            if e.message.startswith('Message_id_invalid'):
                pass
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

    # Name and description
    lines = []
    lines.append(f'*{poll.name}*')
    lines.append(f'_{poll.description}_')

    # All options with their respective people percentage
    for poll_option in poll.options:
        lines.append('')
        if len(poll_option.votes) != 0:
            lines.append(f'*{poll_option.name}* ({len(poll_option.votes)} votes)')
        else:
            lines.append(f'*{poll_option.name}*')
        lines.append(calculate_percentage_line(poll_option, total_user_count))

        if not poll.anonymous:
            for index, vote in enumerate(poll_option.votes):
                if index != len(poll.votes) - 1:
                    line = f'├ {vote.user.name}'
                else:
                    line = f'└ {vote.user.name}'

                lines.append(line)

    # Total user count information
    if total_user_count > 1:
        lines.append(f'\n*{total_user_count} users* voted so far')
    elif total_user_count == 1:
        lines.append('\n*One user* voted so far')

    # Notify users that poll is closed
    if poll.closed:
        lines.insert(0, '⚠️ *This poll is closed* ⚠️\n')
        lines.append('\n⚠️ *This poll is closed* ⚠️')

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

    # Poll is closed, the options are not important any longer
    if poll.closed:
        return poll_text

    management_text = 'Manage your poll:\n\n'
    management_text += poll_text

    return management_text


def get_options_text(poll):
    """Compile the options text for this poll."""
    return f"""*Current options for this poll:*

*Vote type*: {VoteTypeTranslation[poll.vote_type]}
*Anonymity*: {'Names are not visible' if poll.anonymous else 'Names are visible'}

"""
