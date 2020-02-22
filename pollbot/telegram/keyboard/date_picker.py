"""Reply keyboards."""
import calendar
from datetime import date
from telethon import Button

from pollbot.i18n import i18n
from pollbot.helper.enums import CallbackType, DatepickerContext


def get_creation_datepicker_keyboard(poll, current_date):
    """Get the done keyboard for options during poll creation."""
    locale = poll.user.locale
    buttons = get_buttons(poll, current_date, DatepickerContext.creation)

    # Create back and done buttons
    close_payload = f'{CallbackType.close_creation_datepicker.value}:{poll.id}:0'
    row = [Button.inline(i18n.t('keyboard.close', locale=locale), data=close_payload)]
    if len(poll.options) > 0:
        done_payload = f'{CallbackType.all_options_entered.value}:{poll.id}:0'
        row.append(Button.inline(i18n.t('keyboard.done', locale=locale), data=done_payload))
    buttons.append(row)

    return buttons


def get_add_option_datepicker_keyboard(poll, current_date):
    """Get the done keyboard for options during poll creation."""
    from pollbot.telegram.keyboard.settings import get_back_to_settings_button

    buttons = get_buttons(poll, current_date, DatepickerContext.additional_option)
    # Add back to settings button
    row = [get_back_to_settings_button(poll)]
    buttons.append(row)

    return buttons


def get_due_date_datepicker_keyboard(poll, current_date):
    """Get the done keyboard for options during poll creation."""
    from pollbot.telegram.keyboard.settings import get_back_to_settings_button

    buttons = get_buttons(poll, current_date, DatepickerContext.due_date)
    # Add back to settings button
    row = [get_back_to_settings_button(poll)]
    buttons.append(row)

    return buttons


def get_external_datepicker_keyboard(poll, current_date):
    """Get the done keyboard for options during poll creation."""
    buttons = get_buttons(poll, current_date, DatepickerContext.external_add_option)

    # Add back and pick buttons
    back_payload = f'{CallbackType.external_open_menu.value}:{poll.id}:0'
    row = [Button.inline(i18n.t('keyboard.back', locale=poll.locale),
                         data=back_payload)]
    buttons.append(row)

    return buttons


def get_buttons(poll, current_date, datetime_context):
    """Get the buttons for the datepicker.

    Since the datepicker is used in several different scenarios, we allow to dynamically
    set the callback type for date and the weekday(Mo, Di, etc) buttons.
    This is done by setting the datetime_context, which then determines the kind of keyboard.

    This allows us to reuse the keyboard code while moving all handling logic to dedicated
    callback handler functions.
    """
    month = current_date.replace(day=1)
    pick_type, weekday_type, context, picked_dates = resolve_context(poll, datetime_context)

    buttons = []

    ignore_payload = f'{CallbackType.ignore.value}:0:0'

    # Add headline
    headline = f'{calendar.month_name[current_date.month]} {current_date.year}'
    buttons.append([Button.inline(headline, data=ignore_payload)])

    # Create the week-day column description
    row = []
    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        weekday_payload = f'{weekday_type}:{poll.id}:{month.isoformat()}:{day}'
        row.append(Button.inline(day, data=ignore_payload))
    buttons.append(row)

    # Iterate through all days and create respective buttons
    calendar_month = calendar.monthcalendar(current_date.year, current_date.month)
    for week in calendar_month:
        row = []
        for day in week:
            # Format the text. The currently chosen day should be surrounded by brackets e.g (26)
            day_text = str(day)
            if day > 0:
                this_date = date(year=current_date.year, month=current_date.month, day=day)
                if this_date in picked_dates:
                    day_text = f'[{day}]'

            # Only create real buttons for actual days of the month
            if(day == 0):
                row.append(Button.inline(" ", data=ignore_payload))
            else:
                day_date = date(current_date.year, current_date.month, day)
                payload = f'{pick_type}:{poll.id}:{day_date.isoformat()}'
                row.append(Button.inline(day_text, data=payload))

        buttons.append(row)

    # This is a little ugly, but prevents a lot of code duplication
    # Instead of using two callback types for each possible datepicker type, we reuse the same type
    # and store the context as an int at the end of the payload
    # Even though, this breaks our normal format with three values per payload.
    previous_payload = f'{CallbackType.previous_month.value}:{poll.id}:{month.isoformat()}:{context}'
    next_payload = f'{CallbackType.next_month.value}:{poll.id}:{month.isoformat()}:{context}'
    buttons.append([
        Button.inline('<', data=previous_payload),
        Button.inline('>', data=next_payload),
    ])

    return buttons


def resolve_context(poll, context):
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
