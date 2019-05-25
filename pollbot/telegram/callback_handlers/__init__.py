"""Callback query handling."""
from telegram.ext import run_async

from pollbot.helper.session import hidden_session_wrapper
from pollbot.helper.tag import initialize_set_tagging
from pollbot.helper.callback import CallbackType
from pollbot.models import (
    Chat,
    InlineQuery,
    Sticker,
    StickerUsage,
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

        # Get chat entity and telegram chat
        self.chat = session.query(Chat).get(self.query.message.chat.id)
        self.tg_chat = self.query.message.chat


@run_async
@hidden_session_wrapper()
def handle_callback_query(bot, update, session, user):
    """Handle callback queries from inline keyboards."""
    context = CallbackContext(session, update.callback_query, user)
    callback_type = context.callback_type

    return


@run_async
@hidden_session_wrapper()
def handle_chosen_inline_result(bot, update, session, user):
    """Save the chosen inline result."""
