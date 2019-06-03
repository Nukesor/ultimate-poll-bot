"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.telegram.keyboard import get_back_to_management_button
from pollbot.helper.enums import (
    CallbackType,
    CallbackResult,
    UserSorting,
    OptionSorting,
    SortOptionTranslation,
)


def get_back_to_options_button(poll):
    """Get the back to options menu button for option sub menus."""
    payload = f'{CallbackType.menu_back.value}:{poll.id}:{CallbackResult.options.value}'
    return InlineKeyboardButton(text='Back', callback_data=payload)


def get_anonymization_confirmation_keyboard(poll):
    """Get the confirmation keyboard for poll deletion."""
    payload = f'{CallbackType.settings_anonymization.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(text='⚠️ Permanently anonymize poll! ⚠️', callback_data=payload)],
        [get_back_to_management_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_options_keyboard(poll):
    """Get the options menu for this poll."""
    buttons = []
    # Anonymization
    if not poll.anonymous:
        text = "Make votes anonymous"
        payload = f'{CallbackType.settings_anonymization_confirmation.value}:{poll.id}:0'
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    # Sorting sub menu
    text = '🗒 Sorting settings'
    payload = f'{CallbackType.settings_show_sorting.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    # Back button
    buttons.append([get_back_to_management_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_option_sorting_keyboard(poll):
    """Get a keyboard for sorting options."""
    buttons = []

    # Compile the possible options for user sorting
    if not poll.anonymous:
        for order in UserSorting:
            if order.name == poll.user_sorting:
                continue

            button = InlineKeyboardButton(
                text=f'Order users {SortOptionTranslation[order.name]}',
                callback_data=f'{CallbackType.settings_user_sorting.value}:{poll.id}:{order.value}'
            )
            buttons.append([button])

    # Compile the possible options for option sorting
    for order in OptionSorting:
        if order.name == poll.option_sorting:
            continue

        button = InlineKeyboardButton(
            text=f'Order options {SortOptionTranslation[order.name]}',
            callback_data=f'{CallbackType.settings_option_sorting.value}:{poll.id}:{order.value}'
        )
        buttons.append([button])

    buttons.append([get_back_to_options_button(poll)])

    return InlineKeyboardMarkup(buttons)
