"""The start command handler."""
from sqlalchemy.orm.scoping import scoped_session
from telegram.bot import Bot
from telegram.error import BadRequest
from telegram.update import Update

from pollbot.i18n import i18n
from pollbot.models import Notification, Poll
from pollbot.models.user import User
from pollbot.telegram.keyboard.external import get_notify_keyboard
from pollbot.telegram.session import message_wrapper


@message_wrapper()
def notify(bot: Bot, update: Update, session: scoped_session, user: User) -> None:

    """Activate notifications for polls with due date."""
    polls = (
        session.query(Poll)
        .filter(Poll.user == user)
        .filter(Poll.closed.is_(False))
        .filter(Poll.due_date.isnot(None))
        .all()
    )

    select_message = update.message.chat.send_message(
        i18n.t("external.notification.pick_poll", locale=user.locale),
        parse_mode="markdown",
        reply_markup=get_notify_keyboard(polls),
    )

    message = update.message

    notification = (
        session.query(Notification)
        .filter(Notification.chat_id == message.chat.id)
        .filter(Notification.poll_id.is_(None))
        .one_or_none()
    )

    # Try to invalidate the old notification board
    # If this fails, the old message has probably been deleted.
    # Because of this, just ignore this exception in case a BadRequest appears.
    if notification is not None:
        try:
            bot.edit_message_text(
                i18n.t(
                    "external.notification.new_notification_board", locale=user.locale
                ),
                message.chat.id,
                notification.select_message_id,
            )
        except BadRequest:
            pass

    else:
        # Create a new notification to save the reply_to message_id
        # The poll will be created later on
        notification = Notification(message.chat.id)
        session.add(notification)

    if message.reply_to_message is not None:
        poll_message = message.reply_to_message
        notification.poll_message_id = poll_message.message_id
    else:
        notification.poll_message_id = None

    notification.select_message_id = select_message.message_id
