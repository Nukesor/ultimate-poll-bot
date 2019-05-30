"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType, CallbackResult


def get_back_to_management_button(poll):
    """Get the back to management button for poll management sub options."""
    payload = f'{CallbackType.menu_back.value}:{poll.id}:{CallbackResult.main_menu.value}'
    return InlineKeyboardButton(text='Back', callback_data=payload)


def get_management_keyboard(poll):
    """Get the management keyboard for this poll."""
    if poll.closed:
        payload = f'{CallbackType.reopen.value}:{poll.id}:0'
        buttons = [[InlineKeyboardButton(text='Reopen poll', callback_data=payload)]]
        return InlineKeyboardMarkup(buttons)

    vote_payload = f'{CallbackType.menu_vote.value}:{poll.id}:0'
    option_payload = f'{CallbackType.menu_option.value}:{poll.id}:0'
    delete_payload = f'{CallbackType.menu_delete.value}:{poll.id}:0'
    close_payload = f'{CallbackType.close.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(text='Share this poll', switch_inline_query=poll.name)],
        [
            InlineKeyboardButton(text='Vote', callback_data=vote_payload),
            InlineKeyboardButton(text='Options', callback_data=option_payload),
        ],
        [
            InlineKeyboardButton(text='Delete', callback_data=delete_payload),
            InlineKeyboardButton(text='Close', callback_data=close_payload),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def get_deletion_confirmation(poll):
    """Get the confirmation keyboard for poll deletion."""
    payload = f'{CallbackType.delete.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(text='Permanently delete poll!', callback_data=payload)],
        [get_back_to_management_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_options_keyboard(poll):
    """Get the options menu for this poll."""
