"""All keyboards for external users that don't own the poll."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.telegram.keyboard.date_picker import get_datepicker_buttons
from pollbot.helper.enums import (
    CallbackType,
)


def get_external_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    datepicker_buttons = get_datepicker_buttons(poll)

    # Add back and pick buttons
    pick_payload = f'{CallbackType.pick_date_option.value}:{poll.id}:0'
    row = [
        InlineKeyboardButton(text='Pick this date', callback_data=pick_payload),
    ]
    datepicker_buttons.append(row)

    return InlineKeyboardMarkup(datepicker_buttons)


def get_notify_keyboard(polls):
    """Get the keyboard for activationg notifications in a chat."""
    # Add back and pick buttons
    buttons = []
    for poll in polls:
        pick_payload = f'{CallbackType.activate_notification.value}:{poll.id}:0'
        buttons.append([
            InlineKeyboardButton(text=poll.name, callback_data=pick_payload),
        ])

    return InlineKeyboardMarkup(buttons)
