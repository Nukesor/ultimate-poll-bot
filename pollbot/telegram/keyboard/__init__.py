"""Reply keyboards."""
from telegram import (
    ReplyKeyboardMarkup,
)
from .creation import * # noqa
from .management import * # noqa
from .vote import * # noqa
from .options import * # noqa


def get_main_keyboard():
    """Get the main keyboard for the current user."""
    buttons = [
        ['/donations', '/list'],
        ['/create'],
    ]
    keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    return keyboard
