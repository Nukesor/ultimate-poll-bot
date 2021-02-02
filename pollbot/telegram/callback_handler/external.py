"""Option for setting the current date of the picker."""
from datetime import date
from pollbot.poll.update import try_update_reference

from pollbot.decorators import poll_required
from pollbot.display.creation import get_datepicker_text
from pollbot.enums import ExpectedInput, ReferenceType
from pollbot.helper.stats import increase_stat
from pollbot.i18n import i18n
from pollbot.models import Notification, Reference, Update
from pollbot.telegram.keyboard.external import get_external_add_option_keyboard
from pollbot.telegram.keyboard.date_picker import get_external_datepicker_keyboard


@poll_required
def activate_notification(session, context, poll):
    """Show to vote type keyboard."""
    user = context.user
    if user != poll.user:
        return "You aren't allowed to do this"

    message = context.query.message
    notification = (
        session.query(Notification)
        .filter(Notification.select_message_id == message.message_id)
        .one_or_none()
    )

    if notification is None:
        raise Exception(f"Got rogue notification board for poll {poll} and user {user}")

    existing_notification = (
        session.query(Notification)
        .filter(Notification.poll == poll)
        .filter(Notification.chat_id == message.chat_id)
        .one_or_none()
    )

    # We already got a notification in this chat for this poll
    # Save the poll message id anyway
    if existing_notification is not None:
        session.delete(notification)
        existing_notification.poll_message_id = notification.poll_message_id
    else:
        notification.poll = poll

    session.commit()
    message.edit_text(i18n.t("external.notification.activated", locale=poll.locale))
    increase_stat(session, "notifications")


@poll_required
def open_external_datepicker(session, context, poll):
    """All options are entered the poll is created."""
    keyboard = get_external_datepicker_keyboard(poll, date.today())
    # Switch from new option by text to new option via datepicker
    message = context.query.message
    if context.user.expected_input != ExpectedInput.new_user_option.name:
        message.edit_text(
            i18n.t("creation.option.finished", locale=context.user.locale)
        )
        return

    message.edit_text(
        get_datepicker_text(poll), parse_mode="markdown", reply_markup=keyboard
    )


@poll_required
def open_external_menu(session, context, poll):
    """All options are entered the poll is created."""
    context.user.expected_input = ExpectedInput.new_user_option.name
    context.user.current_poll = poll
    session.commit()

    context.query.message.edit_text(
        i18n.t("creation.option.first", locale=poll.locale),
        parse_mode="markdown",
        reply_markup=get_external_add_option_keyboard(poll),
    )


@poll_required
def external_cancel(session, context, poll):
    """All options are entered the poll is created."""
    context.user.expected_input = None
    context.user.current_poll = None
    session.commit()

    context.query.message.edit_text(i18n.t("external.done", locale=poll.locale))


@poll_required
def update_shared(session, context, poll):
    """All options are entered the poll is created."""
    message_id = context.query.inline_message_id

    reference = (
        session.query(Reference)
        .filter(Reference.bot_inline_message_id == message_id)
        .filter(Reference.poll == poll)
        .one_or_none()
    )

    if reference is None:
        reference = Reference(
            poll,
            ReferenceType.inline.name,
            inline_message_id=message_id,
        )
        session.add(reference)
        session.commit()

    try_update_reference(session, context.bot, poll, reference)
