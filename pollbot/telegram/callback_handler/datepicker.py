"""Option for setting the current date of the picker."""
from datetime import date
from dateutil.relativedelta import relativedelta
from pollbot.helper import poll_required
from pollbot.helper.creation import add_options
from pollbot.telegram.keyboard import get_creation_datepicker_keyboard
from pollbot.helper.display.creation import get_datepicker_text


def update_creation_datepicker(context):
    """Update the creation datepicker."""
    keyboard = get_creation_datepicker_keyboard(context.poll)
    context.query.message.edit_text(
        get_datepicker_text(context.poll),
        parse_mode='markdown',
        reply_markup=keyboard
    )


@poll_required
def set_date(session, context, poll):
    """Show to vote type keyboard."""
    poll.current_date = date.fromisoformat(context.action)
    update_creation_datepicker(context)
    context.query.answer(f'Date changed: {poll.current_date.isoformat()}')


@poll_required
def set_next_month(session, context, poll):
    """Show to vote type keyboard."""
    poll.current_date += relativedelta(months=1)
    update_creation_datepicker(context)
    context.query.answer(f'Date changed: {poll.current_date.isoformat()}')


@poll_required
def set_previous_month(session, context, poll):
    """Show to vote type keyboard."""
    poll.current_date -= relativedelta(months=1)
    update_creation_datepicker(context)
    context.query.answer(f'Date changed: {poll.current_date.isoformat()}')


@poll_required
def add_creation_date(session, context, poll):
    """Add a date from the datepicker to the poll."""
    option = poll.current_date.isoformat()
    added_options = add_options(poll, option)
    if len(added_options) == 0:
        context.query.answer(f'Date already picked')
    else:
        update_creation_datepicker(context)
        context.query.answer(f'Date picked: {poll.current_date.isoformat()}')
