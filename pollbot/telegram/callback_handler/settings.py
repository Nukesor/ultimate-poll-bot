"""Callback functions needed during creation of a Poll."""
from datetime import datetime, date, time
from pollbot.i18n import i18n
from pollbot.helper import poll_required
from pollbot.helper.update import update_poll_messages
from pollbot.display import get_settings_text
from pollbot.display.poll import get_poll_text
from pollbot.display.creation import get_datepicker_text
from pollbot.telegram.keyboard import (
    get_anonymization_confirmation_keyboard,
    get_settings_keyboard,
    get_styling_settings_keyboard,
    get_remove_option_keyboard,
    get_add_option_keyboard,
    get_add_option_datepicker_keyboard,
    get_due_date_datepicker_keyboard,
    get_settings_language_keyboard,
)
from pollbot.helper.enums import ExpectedInput
from pollbot.models import PollOption


def send_settings_message(context):
    """Edit the message of the current context to the settings menu."""
    context.query.message.edit_text(
        text=get_settings_text(context.poll),
        parse_mode='markdown',
        reply_markup=get_settings_keyboard(context.poll)
    )


@poll_required
def show_anonymization_confirmation(session, context, poll):
    """Show the delete confirmation message."""
    context.query.message.edit_text(
        i18n.t('settings.anonymize', locale=poll.user.locale),
        reply_markup=get_anonymization_confirmation_keyboard(poll),
    )


@poll_required
def make_anonymous(session, context, poll):
    """Change the anonymity settings of a poll."""
    poll.anonymous = True

    update_poll_messages(session, context.bot, poll)
    send_settings_message(context)


@poll_required
def open_language_picker(session, context, poll):
    """Open the language picker."""
    keyboard = get_settings_language_keyboard(poll)
    context.query.message.edit_text(
        i18n.t('settings.change_language', locale=poll.user.locale),
        parse_mode='markdown',
        reply_markup=keyboard,
    )


@poll_required
def change_poll_language(session, context, poll):
    """Open the language picker."""
    poll.locale = context.action
    session.commit()
    send_settings_message(context)


@poll_required
def open_due_date_datepicker(session, context, poll):
    """Open the datepicker for setting a due date."""
    poll.user.expected_input = ExpectedInput.due_date.name
    context.query.message.edit_reply_markup(
        reply_markup=get_due_date_datepicker_keyboard(poll)
    )


@poll_required
def pick_due_date(session, context, poll):
    """Add a date from the datepicker to the poll."""
    if poll.current_date <= date.today():
        context.query.answer(
            i18n.t('callback.due_date_in_past', locale=poll.user.locale),
        )
        return
    poll.user.expected_input = None
    due_date = datetime.combine(poll.current_date, time(hour=12, minute=00))
    poll.set_due_date(due_date)
    send_settings_message(context)


@poll_required
def remove_due_date(session, context, poll):
    """Remove the due date from a poll."""
    poll.due_date = None
    poll.next_notification = None
    poll.user.expected_input = ExpectedInput.due_date.name
    context.query.message.edit_text(
        text=get_settings_text(context.poll),
        parse_mode='markdown',
        reply_markup=get_due_date_datepicker_keyboard(poll)
    )


@poll_required
def show_styling_menu(session, context, poll):
    """Show the menu for sorting settings."""
    context.query.message.edit_text(
        get_poll_text(session, context.poll),
        parse_mode='markdown',
        reply_markup=get_styling_settings_keyboard(poll),
        disable_web_page_preview=True,
    )


@poll_required
def expect_new_option(session, context, poll):
    """Send a text and tell the user that we expect a new option."""
    user = context.user
    user.expected_input = ExpectedInput.new_option.name
    user.current_poll = poll

    context.query.message.edit_text(
        text=i18n.t('creation.option.first', locale=user.locale),
        parse_mode='markdown',
        reply_markup=get_add_option_keyboard(poll),
    )


@poll_required
def open_new_option_datepicker(session, context, poll):
    """Send a text and tell the user that we expect a new option."""
    context.query.message.edit_text(
        text=get_datepicker_text(poll),
        parse_mode='markdown',
        reply_markup=get_add_option_datepicker_keyboard(poll),
    )


@poll_required
def show_remove_options_menu(session, context, poll):
    """Show the menu for removing options."""
    keyboard = get_remove_option_keyboard(poll)
    context.query.message.edit_text(
        i18n.t('settings.remove_options', locale=poll.user.locale),
        parse_mode='markdown',
        reply_markup=keyboard,
    )


@poll_required
def remove_option(session, context, poll):
    """Remove the option."""
    session.query(PollOption) \
        .filter(PollOption.id == context.action) \
        .delete()
    session.commit()

    keyboard = get_remove_option_keyboard(poll)
    context.query.message.edit_reply_markup(reply_markup=keyboard)

    update_poll_messages(session, context.bot, poll)


@poll_required
def toggle_allow_new_options(session, context, poll):
    """Toggle the visibility of the percentage bar."""
    poll.allow_new_options = not poll.allow_new_options

    update_poll_messages(session, context.bot, poll)
    send_settings_message(context)
