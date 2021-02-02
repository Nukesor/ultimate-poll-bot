"""Option for setting the current date of the picker."""
from datetime import date, datetime, time

from dateutil.relativedelta import relativedelta

from pollbot.decorators import poll_required
from pollbot.display import get_settings_text
from pollbot.display.creation import get_datepicker_text
from pollbot.enums import DatepickerContext
from pollbot.i18n import i18n
from pollbot.poll.option import add_single_option
from pollbot.poll.update import update_poll_messages
from pollbot.telegram.keyboard.date_picker import (
    get_add_option_datepicker_keyboard,
    get_creation_datepicker_keyboard,
    get_due_date_datepicker_keyboard,
    get_external_datepicker_keyboard,
)


def update_datepicker(context, poll, datepicker_context, current_date):
    """Update the creation datepicker."""
    message = get_datepicker_text(context.poll)
    if datepicker_context == DatepickerContext.creation:
        keyboard = get_creation_datepicker_keyboard(poll, current_date)
    elif datepicker_context == DatepickerContext.additional_option:
        keyboard = get_add_option_datepicker_keyboard(poll, current_date)
    elif datepicker_context == DatepickerContext.external_add_option:
        keyboard = get_external_datepicker_keyboard(poll, current_date)
    elif datepicker_context == DatepickerContext.due_date:
        message = get_settings_text(poll)
        keyboard = get_due_date_datepicker_keyboard(poll, current_date)
    else:
        raise Exception("Unknown DatepickerContext")

    context.query.message.edit_text(
        message,
        parse_mode="markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


def owner_pick_date_option(session, context, poll, datepicker_context):
    """Owner adds or removes a date option."""
    picked_date = date.fromisoformat(context.data[2])

    # Check if we already have this date as option
    existing_option = poll.get_date_option(picked_date)
    # If that's the case, delete it
    if existing_option is not None:
        session.delete(existing_option)
        session.commit()
        message = i18n.t(
            "callback.date_removed", locale=poll.locale, date=picked_date.isoformat()
        )
    else:
        add_single_option(session, poll, context.data[2], True)
        session.commit()
        message = i18n.t(
            "callback.date_picked", locale=poll.locale, date=picked_date.isoformat()
        )

    context.query.answer(message)

    update_datepicker(context, poll, datepicker_context, picked_date.replace(day=1))
    if poll.created:
        update_poll_messages(session, context.bot, poll)


@poll_required
def pick_creation_date(session, context, poll):
    """Pick an option during poll creation."""
    owner_pick_date_option(session, context, poll, DatepickerContext.creation)


@poll_required
def pick_creation_weekday(session, context, poll):
    return


@poll_required
def pick_additional_date(session, context, poll):
    """Pick an option after creating the poll."""
    owner_pick_date_option(session, context, poll, DatepickerContext.additional_option)


@poll_required
def pick_additional_weekday(session, context, poll):
    return


@poll_required
def pick_external_date(session, context, poll):
    """Add or remove a date option during creation."""
    picked_date = date.fromisoformat(context.data[2])

    # Check if we already have this date as option
    existing_option = poll.get_date_option(picked_date)
    # If that's the case, delete it
    if existing_option is not None:
        return i18n.t("callback.date_already_picked", locale=poll.locale)

    add_single_option(session, poll, context.data[2], True)
    message = i18n.t(
        "callback.date_picked", locale=poll.locale, date=picked_date.isoformat()
    )
    context.query.answer(message)

    update_datepicker(
        context, poll, DatepickerContext.external_add_option, picked_date.replace(day=1)
    )
    update_poll_messages(session, context.bot, poll)


@poll_required
def pick_due_date(session, context, poll):
    """Set the due date for a poll."""
    picked_date = date.fromisoformat(context.data[2])
    if picked_date <= date.today():
        return i18n.t("callback.due_date_in_past", locale=poll.user.locale)

    due_date = datetime.combine(picked_date, time(hour=12, minute=00))
    if due_date == poll.due_date:
        poll.set_due_date(None)
        context.query.answer(
            i18n.t("callback.due_date_removed", locale=poll.user.locale)
        )
    else:
        poll.set_due_date(due_date)

    context.query.message.edit_text(
        text=get_settings_text(context.poll),
        parse_mode="markdown",
        reply_markup=get_due_date_datepicker_keyboard(poll, picked_date),
    )


@poll_required
def set_next_month(session, context, poll):
    """Show the datepicker keyboard for the next month."""
    this_month = date.fromisoformat(context.data[2])
    datepicker_context = DatepickerContext(int(context.data[3]))

    next_month = this_month + relativedelta(months=1)
    update_datepicker(context, poll, datepicker_context, next_month)
    return i18n.t(
        "callback.date_changed", locale=poll.locale, date=next_month.isoformat()
    )


@poll_required
def set_previous_month(session, context, poll):
    """Show the datepicker keyboard for the previous month."""
    this_month = date.fromisoformat(context.data[2])
    datepicker_context = DatepickerContext(int(context.data[3]))

    previous_month = this_month - relativedelta(months=1)
    update_datepicker(context, poll, datepicker_context, previous_month)
    return i18n.t(
        "callback.date_changed", locale=poll.locale, date=previous_month.isoformat()
    )
