"""Callback functions needed during creation of a Poll."""
from datetime import date
from typing import Optional

from sqlalchemy.orm.scoping import scoped_session
from telegram.message import Message

from pollbot.decorators import poll_required
from pollbot.display.creation import (
    get_datepicker_text,
    get_init_anonymziation_settings_text,
    get_init_text,
    get_native_poll_merged_text,
    get_poll_type_help_text,
)
from pollbot.enums import ExpectedInput, PollType
from pollbot.exceptions import RollbackException
from pollbot.i18n import i18n
from pollbot.models import Poll
from pollbot.poll.creation import create_poll
from pollbot.telegram.callback_handler.context import CallbackContext
from pollbot.telegram.keyboard.creation import (
    get_change_poll_type_keyboard,
    get_init_keyboard,
    get_init_settings_keyboard,
    get_native_poll_merged_keyboard,
    get_open_datepicker_keyboard,
    get_options_entered_keyboard,
    get_skip_description_keyboard,
)
from pollbot.telegram.keyboard.date_picker import get_creation_datepicker_keyboard

from .user import init_poll


def open_init_text(message: Message, poll: Poll) -> None:
    """Open the initial poll creation message."""
    if poll.created_from_native:
        keyboard = get_native_poll_merged_keyboard(poll)
        message.edit_text(
            get_native_poll_merged_text(poll),
            parse_mode="markdown",
            reply_markup=keyboard,
        )
    else:
        keyboard = get_init_keyboard(poll)
        message.edit_text(
            get_init_text(poll), parse_mode="markdown", reply_markup=keyboard
        )


def open_anonymization_settings(message: Message, poll: Poll) -> None:
    """Open the initial poll anonymization settings."""
    message.edit_text(
        get_init_anonymziation_settings_text(poll),
        parse_mode="markdown",
        reply_markup=get_init_settings_keyboard(poll),
        disable_web_page_preview=True,
    )


@poll_required
def back_to_creation_init(session, context, poll):
    """Open the initial poll creation message."""
    open_init_text(context.query.message, poll)


@poll_required
def open_init_anonymization_settings(session, context, poll):
    """Open the anonymization settings for this poll."""
    open_anonymization_settings(context.query.message, poll)


@poll_required
def ask_description(session, context, poll):
    """Asks user for description of the poll, in case the name was already supplied."""
    context.user.expected_input = ExpectedInput.description.name
    keyboard = get_skip_description_keyboard(poll)
    context.tg_chat.send_message(
        i18n.t("creation.description", locale=context.user.locale),
        reply_markup=keyboard,
    )


@poll_required
def skip_description(session, context, poll):
    """Skip description creation step."""
    if len(poll.options) == 0:
        context.user.expected_input = ExpectedInput.options.name
        session.commit()
        context.query.message.edit_text(
            i18n.t("creation.option.first", locale=context.user.locale),
            reply_markup=get_open_datepicker_keyboard(poll),
        )
    else:
        create_poll(session, poll, context.user, context.tg_chat, context.query.message)


@poll_required
def show_poll_type_keyboard(session, context, poll):
    """Show the keyboard to change poll type."""

    poll = session.query(Poll).get(context.payload)

    keyboard = get_change_poll_type_keyboard(poll)
    context.query.message.edit_text(
        get_poll_type_help_text(poll), parse_mode="markdown", reply_markup=keyboard
    )


@poll_required
def change_poll_type(session, context, poll):
    """Change the vote type of the poll.

    This is only possible at the very beginning of the creation.
    """
    if poll.created:
        return i18n.t("callback.poll_created", locale=context.user.locale)

    poll.poll_type = PollType(context.action).name

    open_init_text(context.query.message, poll)


@poll_required
def toggle_anonymity(session, context, poll):
    """Change the anonymity settings of a poll."""
    if poll.created:
        return i18n.t("callback.poll_already_created", locale=context.user.locale)

    poll.anonymous = not poll.anonymous

    open_anonymization_settings(context.query.message, poll)
    return i18n.t("callback.anonymity_changed", locale=context.user.locale)


@poll_required
def toggle_results_visible(session, context, poll):
    """Change the results visible settings of a poll."""
    if poll.created:
        return i18n.t("callback.poll_already_created", locale=context.user.locale)

    poll.results_visible = not poll.results_visible

    open_anonymization_settings(context.query.message, poll)
    return i18n.t("callback.visibility_changed", locale=context.user.locale)


@poll_required
def all_options_entered(session, context, poll):
    """All options are entered the poll is created."""
    if poll is None or poll.created:
        return

    locale = context.user.locale
    if poll.poll_type in [PollType.limited_vote.name, PollType.cumulative_vote.name]:
        message = context.query.message
        message.edit_text(i18n.t("creation.option.finished", locale=locale))
        context.user.expected_input = ExpectedInput.vote_count.name
        message.chat.send_message(i18n.t("creation.vote_count_request", locale=locale))

        return

    create_poll(
        session, poll, context.user, context.query.message.chat, context.query.message
    )


@poll_required
def open_creation_datepicker(session, context, poll):
    """Open the datepicker during the creation of a poll."""
    keyboard = get_creation_datepicker_keyboard(poll, date.today())
    # Switch from new option by text to new option via datepicker
    message = context.query.message
    if context.user.expected_input != ExpectedInput.options.name:
        message.edit_text(
            i18n.t("creation.option.finished", locale=context.user.locale)
        )
        return

    context.user.expected_input = ExpectedInput.date.name

    text = get_datepicker_text(poll)

    if len(text) > 4000:
        error_message = i18n.t("misc.too_many_options", locale=context.user.locale)
        raise RollbackException(error_message)

    message.edit_text(text, parse_mode="markdown", reply_markup=keyboard)


@poll_required
def close_creation_datepicker(session, context, poll):
    """Close the datepicker during the creation of a poll."""
    user = context.user
    if len(poll.options) == 0:
        text = i18n.t("creation.option.first", locale=user.locale)
        keyboard = get_open_datepicker_keyboard(poll)
    else:
        text = i18n.t("creation.option.next", locale=user.locale)
        keyboard = get_options_entered_keyboard(poll)

    message = context.query.message
    # Replace the message completely, since all options have already been entered
    if user.expected_input != ExpectedInput.date.name:
        message.edit_text(i18n.t("creation.option.finished", locale=user.locale))
        return

    user.expected_input = ExpectedInput.options.name
    message.edit_text(text, parse_mode="markdown", reply_markup=keyboard)


def cancel_creation(session: scoped_session, context: CallbackContext) -> Optional[str]:
    """Cancel the creation of a poll."""
    if context.poll is None:
        return i18n.t("delete.doesnt_exist", locale=context.user.locale)

    session.delete(context.poll)
    session.commit()
    context.query.message.edit_text(
        i18n.t("delete.previous_deleted", locale=context.user.locale)
    )

    init_poll(session, context)
