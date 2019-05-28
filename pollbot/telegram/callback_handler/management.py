"""Callback functions needed during creation of a Poll."""
from pollbot.helper.poll_creation import get_init_text, init_options
from pollbot.helper.keyboard import get_change_poll_type_keyboard, get_init_keyboard
from pollbot.helper.enums import PollType, PollCreationStep

from pollbot.models import Poll


def show_poll_type_keyboard(session, context):
    """Change the initial keyboard to poll type keyboard."""
    poll = session.query(Poll).get(context.payload)

    keyboard = get_change_poll_type_keyboard(poll)
    context.query.message.edit_reply_markup(reply_markup=keyboard)
