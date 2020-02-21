"""Reply keyboards."""
from telethon import Button

from pollbot.i18n import i18n, supported_languages
from pollbot.telegram.keyboard import get_back_to_management_button
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
    return Button.inline(text=i18n.t('keyboard.back', locale=locale), data=payload)


def get_anonymization_confirmation_keyboard(poll):
    """Get the confirmation keyboard for poll deletion."""
    locale = poll.user.locale
    payload = f'{CallbackType.settings_anonymization.value}:{poll.id}:0'
    buttons = [
        [Button.inline(i18n.t('keyboard.permanently_anonymize', locale=locale), data=payload)],
        [get_back_to_settings_button(poll)],
    ]
    return buttons


def get_settings_keyboard(poll):
    """Get the options menu for this poll."""
    buttons = []
    locale = poll.user.locale
    # Anonymization
    if not poll.anonymous:
        text = i18n.t('keyboard.anonymize', locale=locale)
        payload = f'{CallbackType.settings_anonymization_confirmation.value}:{poll.id}:0'
        buttons.append([Button.inline(text=text, data=payload)])

    # Change language
    language_text = i18n.t('keyboard.change_language', locale=locale)
    language_payload = f'{CallbackType.settings_open_language_picker.value}:{poll.id}:0'
    buttons.append([Button.inline(text=language_text, data=language_payload)])

    # Open due date datepicker
    new_option_text = i18n.t('keyboard.due_date', locale=locale)
    new_option_payload = f'{CallbackType.settings_open_due_date_datepicker.value}:{poll.id}:0'
    buttons.append([Button.inline(text=new_option_text, data=new_option_payload)])

    # Sorting sub menu
    styling_text = i18n.t('keyboard.styling', locale=locale)
    styling_payload = f'{CallbackType.settings_show_styling.value}:{poll.id}:0'
    buttons.append([Button.inline(text=styling_text, data=styling_payload)])

    # New option button
    new_option_text = i18n.t('keyboard.new_option', locale=locale)
    new_option_payload = f'{CallbackType.settings_new_option.value}:{poll.id}:0'
    buttons.append([Button.inline(text=new_option_text, data=new_option_payload)])

    # Remove options button
    new_option_text = i18n.t('keyboard.remove_option', locale=locale)
    new_option_payload = f'{CallbackType.settings_show_remove_option_menu.value}:{poll.id}:0'
    buttons.append([Button.inline(text=new_option_text, data=new_option_payload)])

    # Allow user options button
    allow_new_option_text = i18n.t('keyboard.allow_user_options', locale=locale)
    if poll.allow_new_options:
        allow_new_option_text = i18n.t('keyboard.forbid_user_options', locale=locale)
    allow_new_option_payload = f'{CallbackType.settings_toggle_allow_new_options.value}:{poll.id}:0'
    buttons.append([Button.inline(text=allow_new_option_text, data=allow_new_option_payload)])
    # Back button
    buttons.append([get_back_to_management_button(poll)])

    return buttons


def get_styling_settings_keyboard(poll):
    """Get a keyboard for sorting options."""
    buttons = []
    locale = poll.user.locale

    if poll.results_visible and not poll.is_priority():
        # Show/hide percentage
        percentage_text = i18n.t('keyboard.show_percentage', locale=locale)
        if poll.show_percentage:
            percentage_text = i18n.t('keyboard.hide_percentage', locale=locale)
        percentage_payload = f'{CallbackType.settings_toggle_percentage.value}:{poll.id}:0'
        buttons.append([Button.inline(text=percentage_text, data=percentage_payload)])

        # Show/hide option votes
        option_votes_text = i18n.t('keyboard.show_option_votes', locale=locale)
        if poll.show_option_votes:
            option_votes_text = i18n.t('keyboard.hide_option_votes', locale=locale)
        option_votes_payload = f'{CallbackType.settings_toggle_option_votes.value}:{poll.id}:0'
        buttons.append([Button.inline(text=option_votes_text, data=option_votes_payload)])

    # Summarize votes in poll
    if poll.results_visible and not poll.permanently_summarized and not poll.is_priority():
        summarize_text = i18n.t('keyboard.summarize_votes', locale=locale)
        if poll.summarize:
            summarize_text = i18n.t('keyboard.dont_summarize_votes', locale=locale)
        summarize_payload = f'{CallbackType.settings_toggle_summarization.value}:{poll.id}:0'
        buttons.append([Button.inline(text=summarize_text, data=summarize_payload)])

    # Date format styling between US and european
    if poll.has_date_option():
        date_format_text = '📅 yyyy-mm-dd date format' if poll.european_date_format else '📅 dd.mm.yyyy date format'
        date_format_payload = f'{CallbackType.settings_toggle_date_format.value}:{poll.id}:0'
        buttons.append([Button.inline(text=date_format_text, data=date_format_payload)])

    if poll.is_doodle() or poll.is_priority():
        doodle_button_text = i18n.t('keyboard.compact_doodle', locale=locale)
        if poll.compact_buttons:
            doodle_button_text = i18n.t('keyboard.no_compact_doodle', locale=locale)
        doodle_button_payload = f'{CallbackType.settings_toggle_compact_buttons.value}:{poll.id}:0'
        buttons.append([Button.inline(text=doodle_button_text, data=doodle_button_payload)])

    # Compile the possible options for user sorting
    if not poll.anonymous and not poll.is_doodle() and not poll.is_priority():
        for order in UserSorting:
            if order.name == poll.user_sorting:
                continue

            option_name = i18n.t(f'sorting.{order.name}', locale=locale)
            data = f'{CallbackType.settings_user_sorting.value}:{poll.id}:{order.value}'
            button = Button.inline(i18n.t('keyboard.order_users', locale=locale, name=option_name), data=data)
            buttons.append([button])

    # Compile the possible options for option sorting
    for order in OptionSorting:
        if order.name == poll.option_sorting:
            continue

        if order.name == OptionSorting.option_percentage.name and (poll.is_doodle() or poll.is_priority()):
            continue

        option_name = i18n.t(f'sorting.{order.name}', locale=locale)
        data = f'{CallbackType.settings_option_sorting.value}:{poll.id}:{order.value}'
        button = Button.inline(i18n.t('keyboard.order_options', locale=locale, name=option_name), data=data)
        buttons.append([button])

    buttons.append([get_back_to_settings_button(poll)])

    return buttons


def get_remove_option_keyboard(poll):
    """Get a keyboard for removing options."""
    buttons = []
    for option in poll.options:
        data = f'{CallbackType.settings_remove_option.value}:{poll.id}:{option.id}'
        button = Button.inline(text=option.name, data=data)
        buttons.append([button])

    buttons.append([get_back_to_settings_button(poll)])

    return buttons


def get_add_option_keyboard(poll):
    """Get the keyboard for adding a new option after poll creation."""
    locale = poll.user.locale
    datepicker_payload = f'{CallbackType.settings_open_add_option_datepicker.value}:{poll.id}:0'
    buttons = [
        [Button.inline(i18n.t('datepicker.open', locale=locale), data=datepicker_payload)],
        [get_back_to_settings_button(poll)],
    ]

    keyboard = buttons

    return keyboard


def get_settings_language_keyboard(poll):
    """Get a keyboard for sorting options."""
    buttons = []
    # Compile the possible options for user sorting
    for language in supported_languages:
        data = f'{CallbackType.settings_change_poll_language.value}:{poll.id}:{language}'
        button = Button.inline(language, data=data)
        buttons.append([button])

    buttons.append([get_back_to_settings_button(poll)])

    return buttons
