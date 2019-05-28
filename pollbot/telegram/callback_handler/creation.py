"""Callback functions needed during creation of a Poll."""
from pollbot.helper.creation import get_init_text, init_options
from pollbot.helper.enums import PollType, PollCreationStep
from pollbot.helper.display import get_poll_management_text
from pollbot.helper.keyboard import (
    get_change_poll_type_keyboard,
    get_init_keyboard,
    get_vote_keyboard,
)

from pollbot.models import Poll, Reference


def show_poll_type_keyboard(session, context):
    """Change the initial keyboard to poll type keyboard."""
    poll = session.query(Poll).get(context.payload)

    keyboard = get_change_poll_type_keyboard(poll)
    context.query.message.edit_reply_markup(reply_markup=keyboard)


def change_poll_type(session, context):
    """Change the poll type and show the initial keyboard."""
    poll = session.query(Poll).get(context.payload)
    poll.type = PollType(context.action).name

    keyboard = get_init_keyboard(poll)
    context.query.message.edit_text(get_init_text(poll), reply_markup=keyboard)


def toggle_anonymity(session, context):
    """Change the anonymity settingi of a poll."""
    poll = session.query(Poll).get(context.payload)
    poll.anonymous = not poll.anonymous

    keyboard = get_init_keyboard(poll)
    context.query.message.edit_text(get_init_text(poll), reply_markup=keyboard)


def skip_description(session, context):
    """Skip the description step of poll creation."""
    poll = session.query(Poll).get(context.payload)
    init_options(session, context.tg_chat, poll)


def all_options_entered(session, context):
    """All options are entered the poll is finished."""
    poll = session.query(Poll).get(context.payload)
    poll.creation_step = PollCreationStep.done.name

    context.user.current_poll = None
    message = context.tg_chat.send_message(
        get_poll_management_text(session, poll),
        parse_mode='markdown',
        reply_markup=get_vote_keyboard(poll)
    )
    reference = Reference(
        poll,
        admin_chat_id=message.chat.id,
        admin_message_id=message.message_id
    )
    session.add(reference)
    session.commit()
