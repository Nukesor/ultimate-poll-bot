"""Reply keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pollbot.enums import CallbackResult, CallbackType
from pollbot.i18n import i18n, supported_languages
from pollbot.models.poll import Poll

from .management import get_back_to_management_button


def get_back_to_settings_button(poll: Poll) -> InlineKeyboardButton:
    """Get the back to options menu button for option sub menus."""
    locale = poll.user.locale
    payload = (
        f"{CallbackType.menu_back.value}:{poll.id}:{CallbackResult.settings.value}"
    )
    return InlineKeyboardButton(
        text=i18n.t("keyboard.back", locale=locale), callback_data=payload
    )


def get_anonymization_confirmation_keyboard(poll: Poll) -> InlineKeyboardMarkup:
    """Get the confirmation keyboard for poll deletion."""
    locale = poll.user.locale
    payload = f"{CallbackType.settings_anonymization.value}:{poll.id}:0"
    buttons = [
        [
            InlineKeyboardButton(
                i18n.t("keyboard.permanently_anonymize", locale=locale),
                callback_data=payload,
            )
        ],
        [get_back_to_settings_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_settings_keyboard(poll: Poll) -> InlineKeyboardMarkup:
    """Get the options menu for this poll."""
    buttons = []
    locale = poll.user.locale
    # Anonymization
    if not poll.anonymous and not poll.is_priority():
        text = i18n.t("keyboard.anonymize", locale=locale)
        payload = (
            f"{CallbackType.settings_anonymization_confirmation.value}:{poll.id}:0"
        )
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    # Change language
    language_text = i18n.t("keyboard.change_language", locale=locale)
    language_payload = f"{CallbackType.settings_open_language_picker.value}:{poll.id}:0"
    buttons.append(
        [InlineKeyboardButton(text=language_text, callback_data=language_payload)]
    )

    # Open due date datepicker
    new_option_text = i18n.t("keyboard.due_date", locale=locale)
    new_option_payload = (
        f"{CallbackType.settings_open_due_date_datepicker.value}:{poll.id}:0"
    )
    buttons.append(
        [InlineKeyboardButton(text=new_option_text, callback_data=new_option_payload)]
    )

    # Styling sub menu
    styling_text = i18n.t("keyboard.styling.open", locale=locale)
    styling_payload = f"{CallbackType.settings_show_styling.value}:{poll.id}:0"
    buttons.append(
        [InlineKeyboardButton(text=styling_text, callback_data=styling_payload)]
    )

    # New option button
    new_option_text = i18n.t("keyboard.new_option", locale=locale)
    new_option_payload = f"{CallbackType.settings_new_option.value}:{poll.id}:0"
    buttons.append(
        [InlineKeyboardButton(text=new_option_text, callback_data=new_option_payload)]
    )

    # Remove options button
    new_option_text = i18n.t("keyboard.remove_option", locale=locale)
    new_option_payload = (
        f"{CallbackType.settings_show_remove_option_menu.value}:{poll.id}:0"
    )
    buttons.append(
        [InlineKeyboardButton(text=new_option_text, callback_data=new_option_payload)]
    )

    # Allow user options button
    allow_new_option_text = i18n.t("keyboard.allow_user_options", locale=locale)
    if poll.allow_new_options:
        allow_new_option_text = i18n.t("keyboard.forbid_user_options", locale=locale)
    allow_new_option_payload = (
        f"{CallbackType.settings_toggle_allow_new_options.value}:{poll.id}:0"
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=allow_new_option_text, callback_data=allow_new_option_payload
            )
        ]
    )

    # Allow others to share the poll
    allow_sharing_text = i18n.t("keyboard.allow_sharing", locale=locale)
    if poll.allow_sharing:
        allow_sharing_text = i18n.t("keyboard.forbid_sharing", locale=locale)
    allow_sharing_payload = (
        f"{CallbackType.settings_toggle_allow_sharing.value}:{poll.id}:0"
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=allow_sharing_text, callback_data=allow_sharing_payload
            )
        ]
    )

    # Back button
    buttons.append([get_back_to_management_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_remove_option_keyboard(poll: Poll) -> InlineKeyboardMarkup:
    """Get a keyboard for removing options."""
    buttons = []
    for option in poll.options:
        name = option.name
        if len(option.name.strip()) == 0:
            name = f"[empty] -- {option.description}"

        button = InlineKeyboardButton(
            text=name,
            callback_data=f"{CallbackType.settings_remove_option.value}:{poll.id}:{option.id}",
        )
        buttons.append([button])

    buttons.append([get_back_to_settings_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_add_option_keyboard(poll: Poll) -> InlineKeyboardMarkup:
    """Get the keyboard for adding a new option after poll creation."""
    locale = poll.user.locale
    datepicker_payload = (
        f"{CallbackType.settings_open_add_option_datepicker.value}:{poll.id}:0"
    )
    buttons = [
        [
            InlineKeyboardButton(
                i18n.t("datepicker.open", locale=locale),
                callback_data=datepicker_payload,
            )
        ],
        [get_back_to_settings_button(poll)],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard


def get_settings_language_keyboard(poll: Poll) -> InlineKeyboardMarkup:
    """Get a keyboard for sorting options."""
    buttons = []
    # Compile the possible options for user sorting
    for language in supported_languages:
        button = InlineKeyboardButton(
            language,
            callback_data=f"{CallbackType.settings_change_poll_language.value}:{poll.id}:{language}",
        )
        buttons.append([button])

    buttons.append([get_back_to_settings_button(poll)])

    return InlineKeyboardMarkup(buttons)
