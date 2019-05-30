"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType, CallbackResult
from pollbot.telegram.keyboard import get_back_to_management_button


def get_anonymization_confirmation_keyboard(poll):
    """Get the confirmation keyboard for poll deletion."""
    payload = f'{CallbackType.option_anonymization.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(text='⚠️ Permanently anonymize poll! ⚠️', callback_data=payload)],
        [get_back_to_management_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_options_keyboard(poll):
    """Get the options menu for this poll."""
    buttons = []
    if not poll.anonymous:
        text = "Make votes anonymous"
        payload = f'{CallbackType.option_anonymization_confirmation.value}:{poll.id}:0'
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    buttons.append([get_back_to_management_button(poll)])

    return InlineKeyboardMarkup(buttons)
