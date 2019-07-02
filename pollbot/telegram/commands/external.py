"""The start command handler."""
from pollbot.helper.session import session_wrapper
from pollbot.models import Poll, Notification
from pollbot.telegram.keyboard.external import get_notify_keyboard


@session_wrapper()
def notify(bot, update, session, user):
    """Activate notifications for polls with due date."""
    polls = session.query(Poll) \
        .filter(Poll.user == user) \
        .filter(Poll.closed.is_(False)) \
        .filter(Poll.due_date.isnot(None)) \
        .all()

    select_message = update.message.chat.send_message(
        'Pick the correct poll to activate notifications',
        parse_mode='markdown',
        reply_markup=get_notify_keyboard(polls)
    )

    # Create a new notification to save the reply_to message_id
    # The poll will be created later on
    message = update.message
    notification = Notification(message.chat.id)
    session.add(notification)

    if message.reply_to_message is not None:
        poll_message = message.reply_to_message
        notification.poll_message_id = poll_message.message_id

    notification.select_message_id = select_message.message_id
