"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType, CallbackResult, VoteType

from .management import get_back_to_management_button


def get_vote_keyboard(poll, show_back=False):
    """Get the keyboard for actual voting."""
    if poll.closed:
        return None

    if poll.vote_type == VoteType.cumulative_vote.name:
        buttons = get_cumulative_buttons(poll)
    else:
        buttons = get_normal_buttons(poll)

    if show_back:
        buttons.append([get_back_to_management_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_normal_buttons(poll):
    """Get the normal keyboard with one button per option."""
    buttons = []
    vote_button_type = CallbackType.vote.value
    for option in poll.options:
        result = CallbackResult.vote.value
        payload = f'{vote_button_type}:{option.id}:{result}'
        text = f'{option.name} ({len(option.votes)} votes)'
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    return buttons


def get_cumulative_buttons(poll):
    """Get the normal keyboard with one button per option."""
    vote_button_type = CallbackType.vote.value
    vote_yes = CallbackResult.vote_yes.value
    vote_no = CallbackResult.vote_no.value

    buttons = []
    for option in poll.options:
        text = f'{option.name} ({len(option.votes)} votes)'
        yes_payload = f'{vote_button_type}:{option.id}:{vote_yes}'
        no_payload = f'{vote_button_type}:{option.id}:{vote_no}'
        buttons.append([
            InlineKeyboardButton(text='➖', callback_data=no_payload),
            InlineKeyboardButton(text=text, callback_data='{CallbackType.ignore.value}:0:0'),
            InlineKeyboardButton(text='➕', callback_data=yes_payload),
        ])

    return buttons
