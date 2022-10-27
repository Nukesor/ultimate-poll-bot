"""All keyboards for external users that don't own the poll."""
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pollbot.enums import CallbackType
from pollbot.i18n import i18n
from pollbot.models.poll import Poll


def get_notify_keyboard(polls: List[Poll]) -> InlineKeyboardMarkup:
    """Get the keyboard for activationg notifications in a chat."""
    # Add back and pick buttons
    buttons = []
    for poll in polls:
        pick_payload = f"{CallbackType.activate_notification.value}:{poll.id}:0"
        buttons.append([InlineKeyboardButton(poll.name, callback_data=pick_payload)])

    return InlineKeyboardMarkup(buttons)


def get_external_add_option_keyboard(poll: Poll) -> InlineKeyboardMarkup:
    """Get the external keyboard for adding a new option after poll creation."""
    locale = poll.user.locale
    datepicker_payload = f"{CallbackType.external_open_datepicker.value}:{poll.id}:0"
    cancel_payload = f"{CallbackType.external_cancel.value}:{poll.id}:0"
    buttons = [
        [
            InlineKeyboardButton(
                i18n.t("datepicker.open", locale=locale),
                callback_data=datepicker_payload,
            )
        ],
        [
            InlineKeyboardButton(
                i18n.t("keyboard.done", locale=poll.locale),
                callback_data=cancel_payload,
            )
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard


def get_external_share_keyboard(poll: Poll) -> InlineKeyboardMarkup:
    """Allow external users to share a poll."""
    locale = poll.user.locale

    buttons = [
        [
            InlineKeyboardButton(
                i18n.t("keyboard.share", locale=locale),
                switch_inline_query=str(poll.uuid),
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard
