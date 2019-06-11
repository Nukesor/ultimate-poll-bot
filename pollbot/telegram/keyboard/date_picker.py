"""Reply keyboards."""
import calendar
from datetime import date
from telegram import (
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType


def get_datepicker_buttons(poll):
    """Get the buttons for the datepicker."""
    current_date = poll.current_date
    if current_date is None:
        current_date = date.now()
        poll.current_date = current_date

    buttons = []

    ignore_payload = f'{CallbackType.ignore.value}:0:0'

    # Add headline
    headline = f'{calendar.month_name[current_date.month]} {current_date.year}'
    buttons.append([InlineKeyboardButton(text=headline, callback_data=ignore_payload)])

    # Create the week-day column description
    row = []
    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        row.append(InlineKeyboardButton(text=day, callback_data=ignore_payload))
        buttons.append(row)

    # Iterate through all days and create respective buttons
    calendar_month = calendar.monthcalendar(current_date.year, current_date.month)
    for week in calendar_month:
        row = []
        for day in week:
            if(day == 0):
                row.append(InlineKeyboardButton(" ", callback_data=ignore_payload))
            else:
                day_date = date(current_date.year, current_date.month, day)
                payload = f'{CallbackType.set_date.value}:{poll.id}:{day_date.isoformat()}'
                row.append(InlineKeyboardButton(day, callback_data=payload))

        buttons.append(row)

    previous_payload = f'{CallbackType.previous_month.value}:{poll.id}:0'
    next_payload = f'{CallbackType.next_month.value}:{poll.id}:0'
    buttons.append([
        InlineKeyboardButton('<', callback_data=previous_payload),
        InlineKeyboardButton('>', callback_data=next_payload),
    ])

    return buttons
