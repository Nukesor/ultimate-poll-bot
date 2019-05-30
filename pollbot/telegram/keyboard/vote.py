"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType, CallbackResult

from .management import get_back_to_management_button


def get_vote_keyboard(poll, show_back=False):
    """Get the keyboard for actual voting."""
    vote_type = CallbackType.vote.value

    if poll.closed:
        return None

    buttons = []
    for option in poll.options:
        result = CallbackResult.vote.value
        payload = f'{vote_type}:{option.id}:{result}'
        text = f'{option.name} ({len(option.votes)} votes)'
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    if show_back:
        buttons.append([get_back_to_management_button(poll)])

    return InlineKeyboardMarkup(buttons)
