"""All keyboards for external users that don't own the poll."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.i18n import i18n
from pollbot.telegram.keyboard.date_picker import get_datepicker_buttons
from pollbot.helper.enums import (
    CallbackType,
)


def get_external_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    datepicker_buttons = get_datepicker_buttons(poll)

    # Add back and pick buttons
    pick_payload = f'{CallbackType.pick_date_option.value}:{poll.id}:0'
    back_payload = f'{CallbackType.external_open_menu.value}:{poll.id}:0'
    cancel_payload = f'{CallbackType.external_cancel.value}:{poll.id}:0'
    rows = [
        [
            InlineKeyboardButton(i18n.t('keyboard.back', locale=poll.locale),
                                 callback_data=back_payload),
            InlineKeyboardButton(i18n.t('keyboard.cancel', locale=poll.locale),
                                 callback_data=cancel_payload)
        ],
        [InlineKeyboardButton(i18n.t('datepicker.pick_date', locale=poll.locale),
                              callback_data=pick_payload)],
    ]
    datepicker_buttons += rows

    return InlineKeyboardMarkup(datepicker_buttons)


def get_notify_keyboard(polls):
    """Get the keyboard for activationg notifications in a chat."""
    # Add back and pick buttons
    buttons = []
    for poll in polls:
        pick_payload = f'{CallbackType.activate_notification.value}:{poll.id}:0'
        buttons.append([
            InlineKeyboardButton(poll.name, callback_data=pick_payload),
        ])

    return InlineKeyboardMarkup(buttons)


def get_external_add_option_keyboard(poll):
    """Get the external keyboard for adding a new option after poll creation."""
    locale = poll.user.locale
    datepicker_payload = f'{CallbackType.external_open_datepicker.value}:{poll.id}:0'
    cancel_payload = f'{CallbackType.external_cancel.value}:{poll.id}:0'
    buttons = [
        [InlineKeyboardButton(i18n.t('keyboard.cancel', locale=poll.locale),
                              callback_data=cancel_payload)],
        [InlineKeyboardButton(i18n.t('datepicker.open', locale=locale),
                              callback_data=datepicker_payload)]]

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard
