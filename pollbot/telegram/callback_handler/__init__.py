"""Callback query handling."""
from telegram.ext import run_async

from pollbot.helper.session import hidden_session_wrapper
from pollbot.helper.enums import CallbackType

from .poll_creation import (
    toggle_anonymity,
    change_poll_type,
    show_poll_type_keyboard,
    skip_description,
    all_options_entered,
)


class CallbackContext():
    """Contains all important information for handling with callbacks."""

    def __init__(self, session, query, user):
        """Create a new CallbackContext from a query."""
        self.query = query
        self.user = user
        data = self.query.data

        # Extract the callback type, task id
        data = data.split(':')
        self.callback_type = int(data[0])
        self.payload = data[1]
        self.action = int(data[2])
        self.callback_name = CallbackType(self.callback_type).name

        # Get chat entity and telegram chat
        self.tg_chat = self.query.message.chat


@run_async
@hidden_session_wrapper()
def handle_callback_query(bot, update, session, user):
    """Handle callback queries from inline keyboards."""
    context = CallbackContext(session, update.callback_query, user)

    if context.callback_name == CallbackType.show_poll_type_keyboard.name:
        show_poll_type_keyboard(session, context)
    elif context.callback_name == CallbackType.change_poll_type.name:
        change_poll_type(session, context)
    elif context.callback_name == CallbackType.toggle_anonymity.name:
        toggle_anonymity(session, context)
    elif context.callback_name == CallbackType.skip_description.name:
        skip_description(session, context)
    elif context.callback_name == CallbackType.all_options_entered.name:
        all_options_entered(session, context)

    return


@run_async
@hidden_session_wrapper()
def handle_chosen_inline_result(bot, update, session, user):
    """Save the chosen inline result."""
