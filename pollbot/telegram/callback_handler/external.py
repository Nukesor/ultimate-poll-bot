"""Option for setting the current date of the picker."""
from datetime import date
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.scoping import scoped_session

from pollbot.decorators import poll_required
from pollbot.display.creation import get_datepicker_text
from pollbot.enums import ExpectedInput, ReferenceType
from pollbot.helper.stats import increase_stat
from pollbot.i18n import i18n
from pollbot.models import Notification, Reference
from pollbot.models.poll import Poll
from pollbot.poll.update import try_update_reference
from pollbot.telegram.callback_handler.context import CallbackContext
from pollbot.telegram.keyboard.date_picker import get_external_datepicker_keyboard
from pollbot.telegram.keyboard.external import get_external_add_option_keyboard


@poll_required
def activate_notification(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> Optional[str]:
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
def open_external_datepicker(
    _: scoped_session, context: CallbackContext, poll: Poll
) -> Optional[str]:
    """This opens the datepicker for non-admin users when they're adding options."""
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
def open_external_menu(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """This opens the option adding menu for non-admin users."""
    context.user.expected_input = ExpectedInput.new_user_option.name
    context.user.current_poll = poll
    session.commit()

    context.query.message.edit_text(
        i18n.t("creation.option.first", locale=poll.locale),
        parse_mode="markdown",
        reply_markup=get_external_add_option_keyboard(poll),
    )


@poll_required
def external_cancel(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Closes the option adding menu for non-admin users."""
    context.user.expected_input = None
    context.user.current_poll = None
    session.commit()

    context.query.message.edit_text(i18n.t("external.done", locale=poll.locale))


@poll_required
def update_shared(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Fallback button to update a poll that might not sync after sharing.

    It might happen due to bugs or network errors, that polls don't get automatically
    synced, once they're shared. For that reason, a button is displayed below the initial
    message, which can be used to trigger a manual update.
    """
    message_id = context.query.inline_message_id

    reference = (
        session.query(Reference)
        .filter(Reference.bot_inline_message_id == message_id)
        .filter(Reference.poll == poll)
        .one_or_none()
    )

    # In case something went wrong and the reference hasn't been created, we have
    # to try it once more in here.
    if reference is None:
        try:
            reference = Reference(
                poll,
                ReferenceType.inline.name,
                inline_message_id=message_id,
            )
            session.add(reference)
            session.commit()
        except IntegrityError:
            # Users can spam this button, which leads to UniqueConstraint errors.
            # Just ignore those.
            session.rollback()

    try_update_reference(session, context.bot, poll, reference)
