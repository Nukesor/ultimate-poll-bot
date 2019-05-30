"""Callback functions needed during creation of a Poll."""
from pollbot.helper.display import update_poll_messages

from pollbot.helper.display import get_options_text
from pollbot.telegram.keyboard import (
    get_options_keyboard,
    get_anonymization_confirmation_keyboard,
)


def show_anonymization_confirmation(session, context):
    """Show the delete confirmation message."""
    context.query.message.edit_text(
        'Do you really want to anonymize this poll?\n⚠️ This action is unrevertable. ⚠️',
        reply_markup=get_anonymization_confirmation_keyboard(context.poll),
    )


def make_anonymous(session, context):
    """Change the anonymity settings of a poll."""
    context.poll.anonymous = True

    context.query.message.edit_text(
        get_options_text(context.poll),
        parse_mode='markdown',
        reply_markup=get_options_keyboard(context.poll)
    )

    update_poll_messages(session, context.bot, context.poll)
