"""Option for setting the current date of the picker."""
from datetime import date
from pollbot.i18n import i18n
from pollbot.helper import poll_required
from pollbot.models import Notification
from pollbot.helper.enums import ExpectedInput
from pollbot.helper.stats import increase_stat
from pollbot.display.creation import get_datepicker_text

from pollbot.telegram.keyboard import (
    get_external_datepicker_keyboard,
    get_external_add_option_keyboard,
)


@poll_required
async def activate_notification(session, context, event, poll):
    """Show to vote type keyboard."""
    user = context.user
    if user != poll.user:
        return "You aren't allowed to do this"

    notification = session.query(Notification) \
        .filter(Notification.select_message_id == event.message_id) \
        .one_or_none()

    if notification is None:
        raise Exception(f"Got rogue notification board for poll {poll} and user {user}")

    existing_notification = session.query(Notification) \
        .filter(Notification.poll == poll) \
        .filter(Notification.chat_id == event.get_message().to_id) \
        .one_or_none()

    # We already got a notification in this chat for this poll
    # Save the poll message id anyway
    if existing_notification is not None:
        session.delete(notification)
        existing_notification.poll_message_id = notification.poll_message_id
    else:
        notification.poll = poll

    session.commit()
    await event.edit(i18n.t('external.notification.activated', locale=poll.locale))
    increase_stat(session, 'notifications')


@poll_required
async def open_external_datepicker(session, context, event, poll):
    """All options are entered the poll is created."""
    keyboard = get_external_datepicker_keyboard(poll, date.today())
    # Switch from new option by text to new option via datepicker
    if context.user.expected_input != ExpectedInput.new_user_option.name:
        await event.edit(i18n.t('creation.option.finished', locale=context.user.locale))
        return

    await event.edit(get_datepicker_text(poll), buttons=keyboard)


@poll_required
async def open_external_menu(session, context, event, poll):
    """All options are entered the poll is created."""
    context.user.expected_input = ExpectedInput.new_user_option.name
    context.user.current_poll = poll
    session.commit()

    await event.edit(
        i18n.t('creation.option.first', locale=poll.locale),
        buttons=get_external_add_option_keyboard(poll)
    )


@poll_required
async def external_cancel(session, context, event, poll):
    """All options are entered the poll is created."""
    context.user.expected_input = None
    context.user.current_poll = None
    session.commit()

    await event.edit(i18n.t('external.done', locale=poll.locale))
