"""User related keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pollbot.enums import CallbackType
from pollbot.i18n import i18n, supported_languages
from pollbot.models.user import User


def get_back_to_menu_button(user: User) -> InlineKeyboardButton:
    """Get the back to options menu button for option sub menus."""
    payload = f"{CallbackType.user_menu.value}:0:0"
    return InlineKeyboardButton(
        text=i18n.t("keyboard.back", locale=user.locale), callback_data=payload
    )


def get_back_to_settings_button(user: User) -> InlineKeyboardButton:
    """Get the back to options settings button for settings sub menus."""
    payload = f"{CallbackType.user_settings.value}:0:0"
    return InlineKeyboardButton(
        text=i18n.t("keyboard.back", locale=user.locale), callback_data=payload
    )


def get_main_keyboard(user: User) -> InlineKeyboardMarkup:
    """User settings keyboard."""
    buttons = [
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.user.init_poll", locale=user.locale),
                callback_data=f"{CallbackType.init_poll.value}:0:0",
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.settings", locale=user.locale),
                callback_data=f"{CallbackType.user_settings.value}:0:0",
            )
        ],
    ]

    if user.admin:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=i18n.t("keyboard.admin.settings", locale=user.locale),
                    callback_data=f"{CallbackType.admin_settings.value}:0:0",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.user.list_polls", locale=user.locale),
                callback_data=f"{CallbackType.user_list_polls.value}:0:0",
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.show_help", locale=user.locale),
                callback_data=f"{CallbackType.open_help.value}:0:0",
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.help_me_out", locale=user.locale),
                callback_data=f"{CallbackType.donate.value}:0:0",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def get_admin_settings_keyboard(user):
    """Keyboard for admin operations."""
    buttons = [
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.refresh", locale=user.locale),
                callback_data=f"{CallbackType.admin_settings.value}:0:0",
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.admin.plot", locale=user.locale),
                callback_data=f"{CallbackType.admin_plot.value}:0:0",
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.admin.update", locale=user.locale),
                callback_data=f"{CallbackType.admin_update.value}:0:0",
            )
        ],
        [get_back_to_menu_button(user)],
    ]

    return InlineKeyboardMarkup(buttons)


def get_user_settings_keyboard(user: User) -> InlineKeyboardMarkup:
    """Keyboard for admin operations."""
    if user.notifications_enabled:
        notification_text = i18n.t("keyboard.user.disable_notifications")
    else:
        notification_text = i18n.t("keyboard.user.enable_notifications")

    buttons = [
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.change_language", locale=user.locale),
                callback_data=f"{CallbackType.user_language_menu.value}:0:0",
            )
        ],
        [
            InlineKeyboardButton(
                text=notification_text,
                callback_data=f"{CallbackType.user_toggle_notification.value}:0:0",
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.user.list_closed_polls", locale=user.locale),
                callback_data=f"{CallbackType.user_list_closed_polls.value}:0:0",
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.user.delete_all", locale=user.locale),
                callback_data=f"{CallbackType.user_delete_all_confirmation.value}:0:0",
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("keyboard.user.delete_all_closed", locale=user.locale),
                callback_data=f"{CallbackType.user_delete_closed_confirmation.value}:0:0",
            )
        ],
        [get_back_to_menu_button(user)],
    ]

    return InlineKeyboardMarkup(buttons)


def get_user_language_keyboard(user: User) -> InlineKeyboardMarkup:
    """Get user language picker keyboard."""
    buttons = []
    # Compile the possible options for user sorting
    for language in supported_languages:
        button = InlineKeyboardButton(
            language,
            callback_data=f"{CallbackType.user_change_language.value}:0:{language}",
        )
        buttons.append([button])

    buttons.append([get_back_to_settings_button(user)])

    return InlineKeyboardMarkup(buttons)


def get_delete_all_confirmation_keyboard(
    user: User, closed: bool = False
) -> InlineKeyboardMarkup:
    """Get the confirmation keyboard for deleting all (closed) polls."""
    locale = user.locale
    if closed:
        payload = f"{CallbackType.user_delete_closed.value}:0:0"
        text = i18n.t("settings.user.delete_closed", locale=locale)
    else:
        payload = f"{CallbackType.user_delete_all.value}:0:0"
        text = i18n.t("settings.user.delete_all", locale=locale)

    buttons = [
        [InlineKeyboardButton(text, callback_data=payload)],
        [get_back_to_settings_button(user)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_delete_user_confirmation_keyboard(user: User) -> InlineKeyboardMarkup:
    """Get the second confirmation keyboard for deleting all information about the user."""
    text = i18n.t("keyboard.user.delete_me", locale=user.locale)
    payload = f"{CallbackType.user_delete_confirmation.value}:0:0"

    ignore_payload = f"{CallbackType.ignore.value}:0:0"

    buttons = [
        [InlineKeyboardButton("DANGER", callback_data=ignore_payload)],
        [InlineKeyboardButton("NOPE ZONE", callback_data=ignore_payload)],
        [InlineKeyboardButton(text, callback_data=payload)],
        [InlineKeyboardButton("STOP AND READ THE TEXT!", callback_data=ignore_payload)],
        [InlineKeyboardButton("DANGER", callback_data=ignore_payload)],
        [get_back_to_settings_button(user)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_delete_user_final_confirmation_keyboard(user):
    """Get the confirmation keyboard for deleting all information about the user."""
    text = i18n.t("keyboard.user.delete_me", locale=user.locale)
    payload = f"{CallbackType.user_delete.value}:0:0"

    buttons = [
        [InlineKeyboardButton(text, callback_data=payload)],
        [get_back_to_settings_button(user)],
    ]
    return InlineKeyboardMarkup(buttons)
