"""Callback functions needed during creation of a Poll."""
from datetime import date

from sqlalchemy.orm.scoping import scoped_session

from pollbot.decorators import poll_required
from pollbot.display import get_settings_text
from pollbot.display.creation import get_datepicker_text
from pollbot.display.poll.compilation import get_poll_text
from pollbot.enums import ExpectedInput
from pollbot.i18n import i18n
from pollbot.models import Option
from pollbot.models.poll import Poll
from pollbot.poll.update import update_poll_messages
from pollbot.poll.vote import reorder_votes_after_option_delete
from pollbot.telegram.callback_handler.context import CallbackContext
from pollbot.telegram.keyboard.date_picker import (
    get_add_option_datepicker_keyboard,
    get_due_date_datepicker_keyboard,
)
from pollbot.telegram.keyboard.settings import (
    get_add_option_keyboard,
    get_anonymization_confirmation_keyboard,
    get_remove_option_keyboard,
    get_settings_keyboard,
    get_settings_language_keyboard,
)
from pollbot.telegram.keyboard.styling import get_styling_settings_keyboard


def send_settings_message(context: CallbackContext) -> None:
    """Edit the message of the current context to the settings menu."""
    context.query.message.edit_text(
        text=get_settings_text(context.poll),
        parse_mode="markdown",
        reply_markup=get_settings_keyboard(context.poll),
        disable_web_page_preview=True,
    )


@poll_required
def show_anonymization_confirmation(
    _: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Show the delete confirmation message."""
    context.query.message.edit_text(
        i18n.t("settings.anonymize", locale=poll.user.locale),
        reply_markup=get_anonymization_confirmation_keyboard(poll),
    )


@poll_required
def make_anonymous(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Change the anonymity settings of a poll."""
    poll.anonymous = True
    if not poll.show_percentage and not poll.show_option_votes:
        poll.show_percentage = True

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_settings_message(context)


@poll_required
def open_language_picker(
    _: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Open the language picker."""
    keyboard = get_settings_language_keyboard(poll)
    context.query.message.edit_text(
        i18n.t("settings.change_language", locale=poll.user.locale),
        parse_mode="markdown",
        reply_markup=keyboard,
    )


@poll_required
def change_poll_language(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Open the language picker."""
    poll.locale = context.action
    session.commit()
    send_settings_message(context)


@poll_required
def open_due_date_datepicker(
    _: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Open the datepicker for setting a due date."""
    poll.user.expected_input = ExpectedInput.due_date.name
    keyboard = get_due_date_datepicker_keyboard(poll, date.today())
    context.query.message.edit_reply_markup(reply_markup=keyboard)


@poll_required
def show_styling_menu(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Show the menu for sorting settings."""
    context.query.message.edit_text(
        get_poll_text(session, context.poll),
        parse_mode="markdown",
        reply_markup=get_styling_settings_keyboard(poll),
        disable_web_page_preview=True,
    )


@poll_required
def expect_new_option(_: scoped_session, context: CallbackContext, poll: Poll) -> None:
    """Send a text and tell the user that we expect a new option."""
    user = context.user
    user.expected_input = ExpectedInput.new_option.name
    user.current_poll = poll

    context.query.message.edit_text(
        text=i18n.t("creation.option.first", locale=user.locale),
        parse_mode="markdown",
        reply_markup=get_add_option_keyboard(poll),
    )


@poll_required
def open_new_option_datepicker(
    _: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Send a text and tell the user that we expect a new option."""
    keyboard = get_add_option_datepicker_keyboard(poll, date.today())
    context.query.message.edit_text(
        text=get_datepicker_text(poll),
        parse_mode="markdown",
        reply_markup=keyboard,
    )


@poll_required
def show_remove_options_menu(
    _: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Show the menu for removing options."""
    keyboard = get_remove_option_keyboard(poll)
    context.query.message.edit_text(
        i18n.t("settings.remove_options", locale=poll.user.locale),
        parse_mode="markdown",
        reply_markup=keyboard,
    )


@poll_required
def remove_option(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Remove the option."""
    session.query(Option).filter(Option.id == context.action).delete()

    if poll.is_priority():
        reorder_votes_after_option_delete(session, poll)

    session.commit()

    keyboard = get_remove_option_keyboard(poll)
    context.query.message.edit_reply_markup(reply_markup=keyboard)

    update_poll_messages(session, context.bot, poll)


@poll_required
def toggle_allow_new_options(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Toggle the visibility of the percentage bar."""
    poll.allow_new_options = not poll.allow_new_options

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_settings_message(context)


@poll_required
def toggle_allow_sharing(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Toggle the visibility of the percentage bar."""
    poll.allow_sharing = not poll.allow_sharing

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_settings_message(context)
