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
    toggle_results_visible,
)

from .vote import (
    handle_vote,
)

from .menu import (
    go_back,
    show_deletion_confirmation,
    show_close_confirmation,
    show_settings,
    show_vote_menu,
    show_menu,
)
from .management import (
    delete_poll,
    close_poll,
    reopen_poll,
)
from .settings import (
    make_anonymous,
    show_anonymization_confirmation,
    show_sorting_menu,
    set_user_order,
    set_option_order,
    expect_new_option,
    show_remove_options_menu,
    remove_option,
    toggle_percentage,
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

    callback_functions = {
        # Creation
        CallbackType.show_vote_type_keyboard: show_vote_type_keyboard,
        CallbackType.change_vote_type: change_vote_type,
        CallbackType.toggle_anonymity: toggle_anonymity,
        CallbackType.all_options_entered: all_options_entered,
        CallbackType.toggle_results_visible: toggle_results_visible,

        # Voting
        CallbackType.vote: handle_vote,

        # Menu
        CallbackType.menu_back: go_back,
        CallbackType.menu_vote: show_vote_menu,
        CallbackType.menu_option: show_settings,
        CallbackType.menu_delete: show_deletion_confirmation,
        CallbackType.menu_show: show_menu,
        CallbackType.menu_close: show_close_confirmation,

        # Poll management
        CallbackType.delete: delete_poll,
        CallbackType.close: close_poll,
        CallbackType.reopen: reopen_poll,

        # Settings
        CallbackType.settings_anonymization_confirmation: show_anonymization_confirmation,
        CallbackType.settings_anonymization: make_anonymous,
        CallbackType.settings_show_sorting: show_sorting_menu,
        CallbackType.settings_user_sorting: set_user_order,
        CallbackType.settings_option_sorting: set_option_order,
        CallbackType.settings_new_option: expect_new_option,
        CallbackType.settings_show_remove_option_menu: show_remove_options_menu,
        CallbackType.settings_remove_option: remove_option,
        CallbackType.settings_toggle_percentage: toggle_percentage,
    }

    callback_functions[context.callback_type](session, context)

    return
