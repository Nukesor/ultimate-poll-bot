"""Callback query handling."""
from telegram.ext import run_async

from pollbot.helper.session import hidden_session_wrapper
from pollbot.helper.enums import CallbackType, CallbackResult
from pollbot.models import Poll

from .creation import (
    toggle_anonymity,
    change_vote_type,
    show_vote_type_keyboard,
    all_options_entered,
)

from .vote import (
    handle_vote,
)

from .menu import (
    go_back,
    show_deletion_confirmation,
    show_options,
    show_vote_menu,
    show_menu,
)
from .management import (
    delete_poll,
    close_poll,
    reopen_poll,
)
from .options import (
    make_anonymous,
    show_anonymization_confirmation,
)


class CallbackContext():
    """Contains all important information for handling with callbacks."""

    def __init__(self, session, bot, query, user):
        """Create a new CallbackContext from a query."""
        self.bot = bot
        self.query = query
        self.user = user
        data = self.query.data

        # Extract the callback type, task id
        data = data.split(':')
        self.callback_type = int(data[0])
        self.payload = data[1]
        self.action = int(data[2])
        self.callback_type = CallbackType(self.callback_type)

        self.poll = session.query(Poll).get(self.payload)

        # Try to resolve the callback result, if possible
        self.callback_result = None
        try:
            self.callback_result = CallbackResult(self.action)
        except (ValueError, KeyError):
            pass

        if self.query.message:
            # Get chat entity and telegram chat
            self.tg_chat = self.query.message.chat


@run_async
@hidden_session_wrapper()
def handle_callback_query(bot, update, session, user):
    """Handle callback queries from inline keyboards."""
    context = CallbackContext(session, bot, update.callback_query, user)

    # Poll creation
    if context.callback_type == CallbackType.show_vote_type_keyboard:
        show_vote_type_keyboard(session, context)
    elif context.callback_type == CallbackType.change_vote_type:
        change_vote_type(session, context)
    elif context.callback_type == CallbackType.toggle_anonymity:
        toggle_anonymity(session, context)
    elif context.callback_type == CallbackType.all_options_entered:
        all_options_entered(session, context)

    # Voting
    elif context.callback_type == CallbackType.vote:
        handle_vote(session, context)

    # Managment menu navigation
    elif context.callback_type == CallbackType.menu_back:
        go_back(session, context)
    elif context.callback_type == CallbackType.menu_vote:
        show_vote_menu(session, context)
    elif context.callback_type == CallbackType.menu_option:
        show_options(session, context)
    elif context.callback_type == CallbackType.menu_delete:
        show_deletion_confirmation(session, context)
    elif context.callback_type == CallbackType.menu_show:
        show_menu(session, context)

    # Management actions
    elif context.callback_type == CallbackType.delete:
        delete_poll(session, context)
    elif context.callback_type == CallbackType.close:
        close_poll(session, context)
    elif context.callback_type == CallbackType.reopen:
        reopen_poll(session, context)

    # Poll options
    elif context.callback_type == CallbackType.option_anonymization_confirmation:
        show_anonymization_confirmation(session, context)
    elif context.callback_type == CallbackType.option_anonymization:
        make_anonymous(session, context)

    return


@run_async
@hidden_session_wrapper()
def handle_chosen_inline_result(bot, update, session, user):
    """Save the chosen inline result."""
