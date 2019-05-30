"""Callback functions needed during creation of a Poll."""
from pollbot.helper.display import update_poll_messages

from pollbot.helper.display import get_options_text
from pollbot.telegram.keyboard import get_options_keyboard


def toggle_anonymity(session, context):
    """Change the anonymity settings of a poll."""
    poll = context.poll
    poll.anonymous = not poll.anonymous

    context.query.message.edit_text(
        get_options_text(poll),
        parse_mode='markdown',
        reply_markup=get_options_keyboard(poll)
    )

    update_poll_messages(poll)
