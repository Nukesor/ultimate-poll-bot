"""Option for setting the current date of the picker."""
from pollbot.helper import poll_required
from pollbot.models import Notification


@poll_required
def activate_notification(session, context, poll):
    """Show to vote type keyboard."""
    user = context.user
    if user != poll.user:
        context.query.answer("You aren't allowed to do this")

    message = context.query.message
    notification = session.query(Notification) \
        .filter(Notification.select_message_id == message.message_id) \
        .one_or_none()

    if notification is None:
        raise Exception(f"Got rogue notification board for poll {poll} and user {user}")

    existing_notification = session.query(Notification) \
        .filter(Notification.poll == poll) \
        .filter(Notification.chat_id == message.chat_id) \
        .one_or_none()

    # We already got a notification in this chat for this poll
    # Save the poll message id anyway
    if existing_notification:
        session.delete(notification)
        existing_notification.poll_message_id = notification.poll_message_id
    else:
        notification.poll = poll

    session.commit()
    context.query.message.edit_text('Notifications activated')
