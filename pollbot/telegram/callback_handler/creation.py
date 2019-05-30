"""Callback functions needed during creation of a Poll."""
from pollbot.helper.creation import get_init_text, get_vote_type_help_text
from pollbot.helper.enums import VoteType
from pollbot.helper.display import get_poll_management_text
from pollbot.telegram.keyboard import (
    get_change_vote_type_keyboard,
    get_management_keyboard,
    get_init_keyboard,
)

from pollbot.models import Poll, Reference


def show_vote_type_keyboard(session, context):
    """Show to vote type keyboard."""
    poll = session.query(Poll).get(context.payload)

    keyboard = get_change_vote_type_keyboard(poll)
    context.query.message.edit_text(get_vote_type_help_text(poll), parse_mode='markdown', reply_markup=keyboard)


def change_vote_type(session, context):
    """Change the vote type."""
    poll = session.query(Poll).get(context.payload)
    poll.vote_type = VoteType(context.action).name

    keyboard = get_init_keyboard(poll)
    context.query.message.edit_text(get_init_text(poll), parse_mode='markdown', reply_markup=keyboard)


def toggle_anonymity(session, context):
    """Change the anonymity settingi of a poll."""
    poll = session.query(Poll).get(context.payload)
    poll.anonymous = not poll.anonymous

    keyboard = get_init_keyboard(poll)
    context.query.message.edit_text(get_init_text(poll), parse_mode='markdown', reply_markup=keyboard)


def all_options_entered(session, context):
    """All options are entered the poll is created."""
    poll = session.query(Poll).get(context.payload)
    poll.created = True
    poll.expected_input = None
    context.user.current_poll = None

    message = context.tg_chat.send_message(
        get_poll_management_text(session, poll),
        parse_mode='markdown',
        reply_markup=get_management_keyboard(poll)
    )
    reference = Reference(
        poll,
        admin_chat_id=message.chat.id,
        admin_message_id=message.message_id
    )
    session.add(reference)
    session.commit()
