"""Option for setting the current date of the picker."""
from datetime import date
from dateutil.relativedelta import relativedelta
from pollbot.i18n import i18n
from pollbot.helper import poll_required
from pollbot.helper.enums import ExpectedInput
from pollbot.helper.creation import add_options
from pollbot.helper.display.creation import get_datepicker_text
from pollbot.telegram.keyboard import (
    get_creation_datepicker_keyboard,
    get_add_option_datepicker_keyboard,
    get_external_datepicker_keyboard,
    get_due_date_datepicker_keyboard,
)


def update_datepicker(context, poll):
    """Update the creation datepicker."""
    user = context.user
    if True: # poll.created and poll.user != user :
        keyboard = get_external_datepicker_keyboard(context.poll)
    elif poll.created and poll.user == user:
        if poll.user.expected_input == ExpectedInput.due_date.name:
            context.query.message.edit_reply_markup(
                reply_markup=get_due_date_datepicker_keyboard(context.poll)
            )
            return
        else:
            keyboard = get_add_option_datepicker_keyboard(context.poll)
    elif not poll.created:
        keyboard = get_creation_datepicker_keyboard(context.poll)
    else:
        raise Exception('Unknown update constellation in datepicker')

    context.query.message.edit_text(
        get_datepicker_text(context.poll),
        parse_mode='markdown',
        reply_markup=keyboard
    )


@poll_required
def set_date(session, context, poll):
    """Show to vote type keyboard."""
    poll.current_date = date.fromisoformat(context.action)
    update_datepicker(context, poll)
    context.query.answer(i18n.t('callback.date_changed', locale=poll.locale,
                                date=poll.current_date.isoformat()))


@poll_required
def set_next_month(session, context, poll):
    """Show to vote type keyboard."""
    poll.current_date += relativedelta(months=1)
    update_datepicker(context, poll)
    context.query.answer(i18n.t('callback.date_changed', locale=poll.locale,
                                date=poll.current_date.isoformat()))


@poll_required
def set_previous_month(session, context, poll):
    """Show to vote type keyboard."""
    poll.current_date -= relativedelta(months=1)
    update_datepicker(context, poll)
    context.query.answer(i18n.t('callback.date_changed', locale=poll.locale,
                                date=poll.current_date.isoformat()))


@poll_required
def add_date(session, context, poll):
    """Add a date from the datepicker to the poll."""
    option = poll.current_date.isoformat()
    added_options = add_options(poll, option, is_date=True)
    if len(added_options) == 0:
        context.query.answer(i18n.t('callback.date_already_picked', locale=poll.locale))
    else:
        update_datepicker(context, poll)
        context.query.answer(i18n.t('callback.date_picked', locale=poll.locale,
                                    date=poll.current_date.isoformat()))
