from telegram.ext import run_async

from pollbot.helper.session import session_wrapper
from pollbot.display.settings import get_user_settings_text
from pollbot.telegram.keyboard import (
    get_user_settings_keyboard,
)


@run_async
@session_wrapper()
def open_user_settings_command(bot, update, session, user):
    """Open the settings menu for the user."""
    update.message.chat.send_message(
        get_user_settings_text(user),
        reply_markup=get_user_settings_keyboard(user),
        parse_mode='markdown',
    )
