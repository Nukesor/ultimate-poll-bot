"""Reply keyboards."""
import calendar
from datetime import date
from typing import Any, List, Tuple, Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pollbot.enums import CallbackType, DatepickerContext
from pollbot.i18n import i18n
from pollbot.models.poll import Poll


def get_creation_datepicker_keyboard(
    poll: Poll, current_date: date
) -> InlineKeyboardMarkup:
    """Get the done keyboard for options during poll creation."""
    locale = poll.user.locale
    datepicker_buttons = get_datepicker_buttons(
        poll, current_date, DatepickerContext.creation
    )

    # Create back and done buttons
    close_payload = f"{CallbackType.close_creation_datepicker.value}:{poll.id}:0"
    buttons = [
        InlineKeyboardButton(
            i18n.t("keyboard.close", locale=locale), callback_data=close_payload
        )
    ]
    if len(poll.options) > 0:
        done_payload = f"{CallbackType.all_options_entered.value}:{poll.id}:0"
        buttons.append(
            InlineKeyboardButton(
                i18n.t("keyboard.done", locale=locale), callback_data=done_payload
            )
        )
    datepicker_buttons.append(buttons)

    return InlineKeyboardMarkup(datepicker_buttons)


def get_add_option_datepicker_keyboard(
    poll: Poll, current_date: date
) -> InlineKeyboardMarkup:
    """Get the done keyboard for options during poll creation."""
    from pollbot.telegram.keyboard.settings import get_back_to_settings_button

    datepicker_buttons = get_datepicker_buttons(
        poll, current_date, DatepickerContext.additional_option
    )
    # Add back to settings button
    row = [get_back_to_settings_button(poll)]
    datepicker_buttons.append(row)

    return InlineKeyboardMarkup(datepicker_buttons)


def get_due_date_datepicker_keyboard(
    poll: Poll, current_date: date
) -> InlineKeyboardMarkup:
    """Get the done keyboard for options during poll creation."""
    from pollbot.telegram.keyboard.settings import get_back_to_settings_button

    datepicker_buttons = get_datepicker_buttons(
        poll, current_date, DatepickerContext.due_date
    )
    # Add back to settings button
    row = [get_back_to_settings_button(poll)]
    datepicker_buttons.append(row)

    return InlineKeyboardMarkup(datepicker_buttons)


def get_external_datepicker_keyboard(poll, current_date):
    """Get the done keyboard for options during poll creation."""
    datepicker_buttons = get_datepicker_buttons(
        poll, current_date, DatepickerContext.external_add_option
    )

    # Add back and pick buttons
    back_payload = f"{CallbackType.external_open_menu.value}:{poll.id}:0"
    rows = [
        [
            InlineKeyboardButton(
                i18n.t("keyboard.back", locale=poll.locale), callback_data=back_payload
            )
        ]
    ]
    datepicker_buttons += rows

    return InlineKeyboardMarkup(datepicker_buttons)


def get_datepicker_buttons(
    poll: Poll, current_date: date, datetime_context: DatepickerContext
) -> List[List[InlineKeyboardButton]]:
    """Get the buttons for the datepicker.

    Since the datepicker is used in several different scenarios, we allow to dynamically
    set the callback type for date and the weekday(Mo, Di, etc) buttons.
    This is done by setting the datetime_context, which then determines the kind of keyboard.

    This allows us to reuse the keyboard code while moving all handling logic to dedicated
    callback handler functions.
    """
    month = current_date.replace(day=1)
    pick_type, weekday_type, context, picked_dates = resolve_context(
        poll, datetime_context
    )

    buttons = []

    ignore_payload = f"{CallbackType.ignore.value}:0:0"

    # Add headline
    headline = f"{calendar.month_name[current_date.month]} {current_date.year}"
    buttons.append([InlineKeyboardButton(headline, callback_data=ignore_payload)])

    # Create the week-day column description
    row = []
    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        # weekday_payload = f"{weekday_type}:{poll.id}:{month.isoformat()}:{day}"
        row.append(InlineKeyboardButton(day, callback_data=ignore_payload))
    buttons.append(row)

    # Iterate through all days and create respective buttons
    calendar_month = calendar.monthcalendar(current_date.year, current_date.month)
    for week in calendar_month:
        row = []
        for day in week:
            # Format the text. The currently chosen day should be surrounded by brackets e.g (26)
            day_text = day
            if day > 0:
                this_date = date(
                    year=current_date.year, month=current_date.month, day=day
                )
                if this_date in picked_dates:
                    day_text = f"[{day}]"

            # Only create real buttons for actual days of the month
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=ignore_payload))
            else:
                day_date = date(current_date.year, current_date.month, day)
                payload = f"{pick_type}:{poll.id}:{day_date.isoformat()}"
                row.append(InlineKeyboardButton(day_text, callback_data=payload))

        buttons.append(row)

    # This is a little ugly, but prevents a lot of code duplication
    # Instead of using two callback types for each possible datepicker type, we reuse the same type
    # and store the context as an int at the end of the payload
    # Even though, this breaks our normal format with three values per payload.
    previous_payload = (
        f"{CallbackType.previous_month.value}:{poll.id}:{month.isoformat()}:{context}"
    )
    next_payload = (
        f"{CallbackType.next_month.value}:{poll.id}:{month.isoformat()}:{context}"
    )
    buttons.append(
        [
            InlineKeyboardButton("<", callback_data=previous_payload),
            InlineKeyboardButton(">", callback_data=next_payload),
        ]
    )

    return buttons


def resolve_context(
    poll: Poll, context: DatepickerContext
) -> Union[Tuple[int, int, int, List[date]], Tuple[int, int, int, List[Any]]]:
    """Return the CallbackTypes, context variable and picked dates depending on input string."""
    # Compile a list of all existing option dates
    option_dates = []
    for option in poll.options:
        if option.is_date:
            option_dates.append(date.fromisoformat(option.name))

    if context == DatepickerContext.creation:
        return (
            CallbackType.pick_creation_date.value,
            CallbackType.pick_creation_weekday.value,
            DatepickerContext.creation.value,
            option_dates,
        )
    elif context == DatepickerContext.additional_option:
        return (
            CallbackType.pick_additional_date.value,
            CallbackType.pick_additional_weekday.value,
            DatepickerContext.additional_option.value,
            option_dates,
        )
    elif context == DatepickerContext.external_add_option:
        return (
            CallbackType.pick_external_date.value,
            CallbackType.ignore.value,
            DatepickerContext.external_add_option.value,
            option_dates,
        )
    elif context == DatepickerContext.due_date:
        # The due date picker can have a single entry at most
        due_date = []
        if poll.due_date is not None:
            due_date.append(poll.due_date.date())

        return (
            CallbackType.pick_due_date.value,
            CallbackType.ignore.value,
            DatepickerContext.due_date.value,
            due_date,
        )
    else:
        raise Exception(f"Unknown Datepicker context: {context}")
