"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType, CallbackResult


def get_back_to_management_button(poll):
    """Get the back to management menu button for management sub menus."""
    payload = f'{CallbackType.menu_back.value}:{poll.id}:{CallbackResult.main_menu.value}'
    return InlineKeyboardButton(text='Back', callback_data=payload)


def get_management_keyboard(poll):
    """Get the management keyboard for this poll."""
    if poll.deleted:
        return None
    delete_payload = f'{CallbackType.menu_delete.value}:{poll.id}:0'

    if poll.closed and not poll.results_visible:
        return InlineKeyboardMarkup([[InlineKeyboardButton(text='❌ Delete', callback_data=delete_payload)]])
    elif poll.closed:
        reopen_payload = f'{CallbackType.reopen.value}:{poll.id}:0'
        reset_payload = f'{CallbackType.reset.value}:{poll.id}:0'
        clone_payload = f'{CallbackType.clone.value}:{poll.id}:0'
        buttons = [
            [
                InlineKeyboardButton(text='🔨 Reset', callback_data=reset_payload),
                InlineKeyboardButton(text='🧬 Clone', callback_data=clone_payload),
            ],
            [InlineKeyboardButton(text='❌ Delete', callback_data=delete_payload)],
            [InlineKeyboardButton(text='🔓 Reopen poll', callback_data=reopen_payload)]
        ]
        return InlineKeyboardMarkup(buttons)

    vote_payload = f'{CallbackType.menu_vote.value}:{poll.id}:0'
    option_payload = f'{CallbackType.menu_option.value}:{poll.id}:0'
    delete_payload = f'{CallbackType.menu_delete.value}:{poll.id}:0'

    if poll.results_visible:
        close_payload = f'{CallbackType.close.value}:{poll.id}:0'
    else:
        close_payload = f'{CallbackType.menu_close.value}:{poll.id}:0'

    buttons = [
        [
            InlineKeyboardButton(text='Share this poll', switch_inline_query=poll.name),
        ],
        [
            InlineKeyboardButton(text='✉️ Vote', callback_data=vote_payload),
            InlineKeyboardButton(text='⚙️ Settings', callback_data=option_payload),
        ],
        [
            InlineKeyboardButton(text='❌ Delete', callback_data=delete_payload),
            InlineKeyboardButton(text='🔒 Close', callback_data=close_payload),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def get_close_confirmation(poll):
    """Get the confirmation keyboard for closing of a poll."""
    payload = f'{CallbackType.close.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(text='⚠️ Permanently close poll! ⚠️', callback_data=payload)],
        [get_back_to_management_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_deletion_confirmation(poll):
    """Get the confirmation keyboard for poll deletion."""
    payload = f'{CallbackType.delete.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(text='⚠️ Permanently delete poll! ⚠️', callback_data=payload)],
        [get_back_to_management_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_poll_list_keyboard(polls):
    """Get the confirmation keyboard for poll deletion."""
    buttons = []
    for poll in polls:
        payload = f'{CallbackType.menu_show.value}:{poll.id}:0'
        buttons.append([InlineKeyboardButton(text=poll.name, callback_data=payload)])

    return InlineKeyboardMarkup(buttons)
