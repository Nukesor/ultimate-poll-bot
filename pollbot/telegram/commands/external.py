"""The start command handler."""
from telethon import events

from pollbot.i18n import i18n
from pollbot.client import client
from pollbot.helper.session import message_wrapper
from pollbot.helper import get_peer_information
from pollbot.models import Poll, Notification
from pollbot.telegram.keyboard.external import get_notify_keyboard


@client.on(events.NewMessage(incoming=True, pattern='/notify'))
@message_wrapper()
async def notify(event, session, user):
    """Activate notifications for polls with due date."""
    polls = session.query(Poll) \
        .filter(Poll.user == user) \
        .filter(Poll.closed.is_(False)) \
        .filter(Poll.due_date.isnot(None)) \
        .all()

    if len(polls) == 0:
        await event.respond(i18n.t('external.notification.no_active_poll', locale=user.locale))
        raise events.StopPropagation

    select_message = await event.respond(
        i18n.t('external.notification.pick_poll', locale=user.locale),
        buttons=get_notify_keyboard(polls)
    )
    peer_id, _ = get_peer_information(event.to_id)

    notification = session.query(Notification) \
        .filter(Notification.chat_id == peer_id) \
        .filter(Notification.poll_id.is_(None)) \
        .one_or_none()

    # Try to invalidate the old notification board
    # If this fails, the old message has probably been deleted.
    # Because of this, just ignore this exception in case a BadRequest appears.
    if notification is not None:
        await client.edit_message(
            notification.select_message_id,
            i18n.t('external.notification.new_notification_board', locale=user.locale),
        )

    else:
        # Create a new notification to save the reply_to message_id
        # The poll will be created later on
        notification = Notification(peer_id)
        session.add(notification)

    notification.poll_message_id = event.reply_to_msg_id
    notification.select_message_id = select_message.id

    raise events.StopPropagation
