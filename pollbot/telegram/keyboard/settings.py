"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.telegram.keyboard import get_back_to_management_button
from pollbot.telegram.keyboard.date_picker import get_datepicker_buttons
from pollbot.helper.enums import (
    CallbackType,
    CallbackResult,
    UserSorting,
    OptionSorting,
    SortOptionTranslation,
)


def get_back_to_settings_button(poll):
    """Get the back to options menu button for option sub menus."""
    payload = f'{CallbackType.menu_back.value}:{poll.id}:{CallbackResult.settings.value}'
    return InlineKeyboardButton(text='Back', callback_data=payload)


def get_anonymization_confirmation_keyboard(poll):
    """Get the confirmation keyboard for poll deletion."""
    payload = f'{CallbackType.settings_anonymization.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(text='⚠️ Permanently anonymize poll! ⚠️', callback_data=payload)],
        [get_back_to_management_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_settings_keyboard(poll):
    """Get the options menu for this poll."""
    buttons = []
    # Anonymization
    if not poll.anonymous:
        text = "🔍 Make votes anonymous"
        payload = f'{CallbackType.settings_anonymization_confirmation.value}:{poll.id}:0'
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    # Open due date datepicker
    new_option_text = '📅 Set due date'
    new_option_payload = f'{CallbackType.settings_open_due_date_datepicker.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=new_option_text, callback_data=new_option_payload)])

    if poll.has_date_option():
        # Show percentage option
        date_format_text = '📅 yyyy-mm-dd date format' if poll.european_date_format else '📅 dd.mm.yyyy date format'
        date_format_payload = f'{CallbackType.settings_toggle_date_format.value}:{poll.id}:0'
        buttons.append([InlineKeyboardButton(text=date_format_text, callback_data=date_format_payload)])

    # Sorting sub menu
    sorting_text = '📋 Sorting settings'
    sorting_payload = f'{CallbackType.settings_show_sorting.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=sorting_text, callback_data=sorting_payload)])
    if poll.results_visible:
        # Show percentage option
        percentage_text = '○% Hide percentage' if poll.show_percentage else '○% Show percentage'
        percentage_payload = f'{CallbackType.settings_toggle_percentage.value}:{poll.id}:0'
        buttons.append([InlineKeyboardButton(text=percentage_text, callback_data=percentage_payload)])

    # New option button
    new_option_text = '＋ Add a new option'
    new_option_payload = f'{CallbackType.settings_new_option.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=new_option_text, callback_data=new_option_payload)])

    # Remove options button
    new_option_text = '－  Remove options'
    new_option_payload = f'{CallbackType.settings_show_remove_option_menu.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=new_option_text, callback_data=new_option_payload)])

    # Allow user options button
    if poll.allow_new_options:
        allow_new_option_text = "🍺 Forbid users to add new options"
    else:
        allow_new_option_text = '🍻 Allow users to add new options'
    allow_new_option_payload = f'{CallbackType.settings_toggle_allow_new_options.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=allow_new_option_text, callback_data=allow_new_option_payload)])
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

    buttons.append([get_back_to_settings_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_remove_option_keyboad(poll):
    """Get a keyboard for removing options."""
    buttons = []
    for option in poll.options:
        button = InlineKeyboardButton(
            text=option.name,
            callback_data=f'{CallbackType.settings_remove_option.value}:{poll.id}:{option.id}',
        )
        buttons.append([button])

    buttons.append([get_back_to_settings_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_add_option_keyboard(poll):
    """Get the keyboard for adding a new option after poll creation."""
    datepicker_payload = f'{CallbackType.settings_open_add_option_datepicker.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(text='Open Datepicker', callback_data=datepicker_payload)],
        [get_back_to_settings_button(poll)],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard


def get_add_option_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    datepicker_buttons = get_datepicker_buttons(poll)

    # Add back and pick buttons
    pick_payload = f'{CallbackType.pick_date_option.value}:{poll.id}:0'
    row = [
        get_back_to_settings_button(poll),
        InlineKeyboardButton(text='Pick this date', callback_data=pick_payload),
    ]
    datepicker_buttons.append(row)

    return InlineKeyboardMarkup(datepicker_buttons)


def get_due_date_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    datepicker_buttons = get_datepicker_buttons(poll)

    # Add back and pick buttons
    pick_payload = f'{CallbackType.settings_pick_due_date.value}:{poll.id}:0'
    row = [
        get_back_to_settings_button(poll),
        InlineKeyboardButton(text='Set due date', callback_data=pick_payload),
    ]
    datepicker_buttons.append(row)

    return InlineKeyboardMarkup(datepicker_buttons)
