"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType, CallbackResult
from pollbot.telegram.keyboard import get_back_to_management_button


def get_options_keyboard(poll):
    """Get the options menu for this poll."""
    buttons = [
        [get_back_to_management_button(poll)],
    ]

    return InlineKeyboardMarkup(buttons)
