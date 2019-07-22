"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.i18n import i18n, supported_languages
from pollbot.telegram.keyboard import get_back_to_management_button
from pollbot.telegram.keyboard.date_picker import get_datepicker_buttons
from pollbot.helper.enums import (
    CallbackType,
    CallbackResult,
    UserSorting,
    OptionSorting,
)


def get_back_to_settings_button(poll):
    """Get the back to options menu button for option sub menus."""
    locale = poll.user.locale
    payload = f'{CallbackType.menu_back.value}:{poll.id}:{CallbackResult.settings.value}'
    return InlineKeyboardButton(text=i18n.t('keyboard.back', locale=locale),
                                callback_data=payload)


def get_anonymization_confirmation_keyboard(poll):
    """Get the confirmation keyboard for poll deletion."""
    locale = poll.user.locale
    payload = f'{CallbackType.settings_anonymization.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(i18n.t('keyboard.permanently_anonymize', locale=locale),
                              callback_data=payload)],
        [get_back_to_management_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_settings_keyboard(poll):
    """Get the options menu for this poll."""
    buttons = []
    locale = poll.user.locale
    # Anonymization
    if not poll.anonymous:
        text = i18n.t('keyboard.anonymize', locale=locale)
        payload = f'{CallbackType.settings_anonymization_confirmation.value}:{poll.id}:0'
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    # Change language
    language_text = i18n.t('keyboard.change_language', locale=locale)
    language_payload = f'{CallbackType.settings_open_language_picker.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=language_text, callback_data=language_payload)])

    # Open due date datepicker
    new_option_text = i18n.t('keyboard.due_date', locale=locale)
    new_option_payload = f'{CallbackType.settings_open_due_date_datepicker.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=new_option_text, callback_data=new_option_payload)])

    if poll.has_date_option():
        # Show percentage option
        date_format_text = '📅 yyyy-mm-dd date format' if poll.european_date_format else '📅 dd.mm.yyyy date format'
        date_format_payload = f'{CallbackType.settings_toggle_date_format.value}:{poll.id}:0'
        buttons.append([InlineKeyboardButton(text=date_format_text, callback_data=date_format_payload)])

    # Sorting sub menu
    sorting_text = i18n.t('keyboard.sorting', locale=locale)
    sorting_payload = f'{CallbackType.settings_show_sorting.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=sorting_text, callback_data=sorting_payload)])
    if poll.results_visible:
        # Show percentage option
        percentage_text = i18n.t('keyboard.show_percentage', locale=locale)
        if poll.show_percentage:
            percentage_text = i18n.t('keyboard.hide_percentage', locale=locale)
        percentage_payload = f'{CallbackType.settings_toggle_percentage.value}:{poll.id}:0'
        buttons.append([InlineKeyboardButton(text=percentage_text, callback_data=percentage_payload)])

    # New option button
    new_option_text = i18n.t('keyboard.new_option', locale=locale)
    new_option_payload = f'{CallbackType.settings_new_option.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=new_option_text, callback_data=new_option_payload)])

    # Remove options button
    new_option_text = i18n.t('keyboard.remove_option', locale=locale)
    new_option_payload = f'{CallbackType.settings_show_remove_option_menu.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=new_option_text, callback_data=new_option_payload)])

    # Allow user options button
    allow_new_option_text = i18n.t('keyboard.allow_user_options', locale=locale)
    if poll.allow_new_options:
        allow_new_option_text = i18n.t('keyboard.forbid_user_options', locale=locale)
    allow_new_option_payload = f'{CallbackType.settings_toggle_allow_new_options.value}:{poll.id}:0'
    buttons.append([InlineKeyboardButton(text=allow_new_option_text, callback_data=allow_new_option_payload)])
    # Back button
    buttons.append([get_back_to_management_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_option_sorting_keyboard(poll):
    """Get a keyboard for sorting options."""
    buttons = []
    locale = poll.user.locale

    # Compile the possible options for user sorting
    if not poll.anonymous:
        for order in UserSorting:
            if order.name == poll.user_sorting:
                continue

            option_name = i18n.t(f'sorting.{order.name}', locale=locale)
            button = InlineKeyboardButton(
                i18n.t('keyboard.order_users', locale=locale, name=option_name),
                callback_data=f'{CallbackType.settings_user_sorting.value}:{poll.id}:{order.value}'
            )
            buttons.append([button])

    # Compile the possible options for option sorting
    for order in OptionSorting:
        if order.name == poll.option_sorting:
            continue

        option_name = i18n.t(f'sorting.{order.name}', locale=locale)
        button = InlineKeyboardButton(
            i18n.t('keyboard.order_options', locale=locale, name=option_name),
            callback_data=f'{CallbackType.settings_option_sorting.value}:{poll.id}:{order.value}'
        )
        buttons.append([button])

    buttons.append([get_back_to_settings_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_remove_option_keyboard(poll):
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
    locale = poll.user.locale
    datepicker_payload = f'{CallbackType.settings_open_add_option_datepicker.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(
            i18n.t('datepicker.open', locale=locale),
            callback_data=datepicker_payload)],
        [get_back_to_settings_button(poll)],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard


def get_add_option_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    locale = poll.user.locale
    datepicker_buttons = get_datepicker_buttons(poll)
    # Add back and pick buttons
    pick_payload = f'{CallbackType.pick_date_option.value}:{poll.id}:0'
    row = [
        get_back_to_settings_button(poll),
        InlineKeyboardButton(
            i18n.t('datepicker.pick_date', locale=locale),
            callback_data=pick_payload),
    ]
    datepicker_buttons.append(row)

    return InlineKeyboardMarkup(datepicker_buttons)


def get_due_date_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    datepicker_buttons = get_datepicker_buttons(poll)

    # Add back and pick buttons
    locale = poll.user.locale
    pick_payload = f'{CallbackType.settings_pick_due_date.value}:{poll.id}:0'
    row = [
        get_back_to_settings_button(poll),
        InlineKeyboardButton(
            i18n.t('datepicker.due_date', locale=locale),
            callback_data=pick_payload),
    ]
    datepicker_buttons.append(row)

    return InlineKeyboardMarkup(datepicker_buttons)


def get_settings_language_keyboard(poll):
    """Get a keyboard for sorting options."""
    buttons = []
    # Compile the possible options for user sorting
    for language in supported_languages:
        button = InlineKeyboardButton(
            language,
            callback_data=f'{CallbackType.settings_change_poll_language.value}:{poll.id}:{language}'
        )
        buttons.append([button])

    github_url = 'https://github.com/Nukesor/ultimate-poll-bot/tree/master/i18n'
    buttons.append([InlineKeyboardButton(text='Add a new language', url=github_url)])
    buttons.append([get_back_to_settings_button(poll)])

    return InlineKeyboardMarkup(buttons)
