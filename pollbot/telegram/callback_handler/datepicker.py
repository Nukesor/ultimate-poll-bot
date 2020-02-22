"""Option for setting the current date of the picker."""
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pollbot.i18n import i18n
from pollbot.helper import poll_required
from pollbot.helper.enums import DatepickerContext
from pollbot.helper.creation import add_options
from pollbot.helper.update import update_poll_messages
from pollbot.display import get_settings_text
from pollbot.display.creation import get_datepicker_text
from pollbot.telegram.keyboard.date_picker import (
    get_creation_datepicker_keyboard,
    get_add_option_datepicker_keyboard,
    get_external_datepicker_keyboard,
    get_due_date_datepicker_keyboard,
)


async def update_datepicker(context, poll, datepicker_context, current_date):
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
        raise Exception('Unknown DatepickerContext')

    await context.event.edit(
        message,
        buttons=keyboard,
        link_preview=False
    )


async def owner_pick_date_option(session, context, event, poll, datepicker_context):
    """Owner adds or removes a date option."""
    picked_date = date.fromisoformat(context.data[2])

    # Check if we already have this date as option
    existing_option = poll.get_date_option(picked_date)
    # If that's the case, delete it
    if existing_option is not None:
        session.delete(existing_option)
        session.commit()
        message = i18n.t('callback.date_removed', locale=poll.locale,
                         date=picked_date.isoformat())
    else:
        add_options(poll, context.data[2], is_date=True)
        session.commit()
        message = i18n.t('callback.date_picked', locale=poll.locale,
                         date=picked_date.isoformat())
    await event.answer(message)

    await update_datepicker(context, poll, datepicker_context, picked_date.replace(day=1))
    if poll.created:
        await update_poll_messages(session, poll)


@poll_required
async def pick_creation_date(session, context, event, poll):
    """Pick an option during poll creation."""
    await owner_pick_date_option(session, context, event, poll, DatepickerContext.creation)


@poll_required
async def pick_creation_weekday(session, context, event, poll):
    return


@poll_required
async def pick_additional_date(session, context, event, poll):
    """Pick an option after creating the poll."""
    await owner_pick_date_option(session, context, event, poll, DatepickerContext.additional_option)


@poll_required
async def pick_additional_weekday(session, context, event, poll):
    return


@poll_required
async def pick_external_date(session, context, event, poll):
    """Add or remove a date option during creation."""
    picked_date = date.fromisoformat(context.data[2])

    # Check if we already have this date as option
    existing_option = poll.get_date_option(picked_date)
    # If that's the case, delete it
    if existing_option is not None:
        return i18n.t('callback.date_already_picked', locale=poll.locale)

    add_options(poll, context.data[2], is_date=True)
    session.commit()
    message = i18n.t('callback.date_picked', locale=poll.locale,
                     date=picked_date.isoformat())
    await event.answer(message)

    await update_datepicker(
        context,
        poll,
        DatepickerContext.external_add_option,
        picked_date.replace(day=1)
    )
    await update_poll_messages(session, poll)


@poll_required
async def pick_due_date(session, context, event, poll):
    """Set the due date for a poll."""
    picked_date = date.fromisoformat(context.data[2])
    if picked_date <= date.today():
        return i18n.t('callback.due_date_in_past', locale=poll.user.locale)

    due_date = datetime.combine(picked_date, time(hour=12, minute=00))
    if (due_date == poll.due_date):
        poll.set_due_date(None)
        await event.answer(
            i18n.t('callback.due_date_removed', locale=poll.user.locale)
        )
    else:
        poll.set_due_date(due_date)

    await event.edit(
        text=get_settings_text(context.poll),
        buttons=get_due_date_datepicker_keyboard(poll, picked_date)
    )


@poll_required
async def set_next_month(session, context, event, poll):
    """Show the datepicker keyboard for the next month."""
    this_month = date.fromisoformat(context.data[2])
    datepicker_context = DatepickerContext(int(context.data[3]))

    next_month = this_month + relativedelta(months=1)
    await update_datepicker(context, poll, datepicker_context, next_month)
    return i18n.t('callback.date_changed', locale=poll.locale,
                  date=next_month.isoformat())


@poll_required
async def set_previous_month(session, context, event, poll):
    """Show the datepicker keyboard for the previous month."""
    this_month = date.fromisoformat(context.data[2])
    datepicker_context = DatepickerContext(int(context.data[3]))

    previous_month = this_month - relativedelta(months=1)
    await update_datepicker(context, poll, datepicker_context, previous_month)
    return i18n.t('callback.date_changed', locale=poll.locale,
                  date=previous_month.isoformat())
