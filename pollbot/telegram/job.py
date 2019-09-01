"""Handle messages."""
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from telegram.error import BadRequest, Unauthorized
from telegram.ext import run_async

from pollbot.i18n import i18n
from pollbot.models import Update, Notification, Poll
from pollbot.helper.session import job_session_wrapper
from pollbot.helper.update import send_updates, window_size, update_poll_messages


@run_async
@job_session_wrapper()
def message_update_job(context, session):
    """Update all messages if necessary."""
    try:
        context.job.enabled = False
        now = datetime.now()
        current_time_window = now - timedelta(seconds=now.second % window_size,
                                              microseconds=now.microsecond)
        last_time_window = current_time_window - timedelta(seconds=window_size)
        one_minute_ago = current_time_window - timedelta(minutes=1)

        updates = session.query(Update) \
            .filter(Update.updated.is_(False)) \
            .filter(Update.time_window <= last_time_window) \
            .options(joinedload(Update.poll)) \
            .order_by(Update.time_window.desc()) \
            .all()

        polls_for_refresh = []
        for update in updates:
            # It might be that there are multiple active updates
            # due to the job timeouts and multiple repetetive votes
            # or long update tasks/telegram timeouts
            previous_active_updates = session.query(Update) \
                .filter(Update.poll == update.poll) \
                .filter(Update.updated.is_(False)) \
                .all()
            if len(previous_active_updates) >= 0:
                for previous_update in previous_active_updates:
                    previous_update.updated = True
                    polls_for_refresh.append(previous_update.poll_id)
                    session.commit()

            # If a more recent update has alreday been updated, ignore the previous updates
            elif update.poll_id in polls_for_refresh:
                session.refresh(update)
                if update.updated:
                    continue

            # Get the update amount of the last minute
            updates_in_last_minute = session.query(func.sum(Update.count)) \
                .filter(Update.poll == update.poll) \
                .filter(Update.time_window >= one_minute_ago) \
                .one_or_none()[0]
            if updates_in_last_minute is None:
                updates_in_last_minute = 0

            # Smaller 100, because we need a liiiittle bit of buffer. Timings aren't allways perfect
            if updates_in_last_minute < 100:
                send_updates(session, context.bot, update.poll, show_warning=True)
                session.query(Update) \
                    .filter(Update.id == update.id) \
                    .update({
                        'count': Update.count + 1,
                        'updated': True,
                    })

            # Let's wait a little longer
            else:
                pass
    finally:
        context.job.enabled = True
        session.close()


@run_async
@job_session_wrapper()
def send_notifications(context, session):
    """Notify the users about the poll being closed soon."""
    polls = session.query(Poll) \
        .join(Notification.poll) \
        .filter(Poll.next_notification <= datetime.now()) \
        .filter(Poll.closed.is_(False)) \
        .all()

    for poll in polls:
        time_step = poll.due_date - poll.next_notification

        if time_step == timedelta(days=7):
            send_notifications_for_poll(context, session, poll, 'notification.one_week')
            poll.next_notification = poll.due_date - timedelta(days=1)

        # One day remaining reminder
        elif time_step == timedelta(days=1):
            send_notifications_for_poll(context, session, poll, 'notification.one_day')
            poll.next_notification = poll.due_date - timedelta(hours=6)

        # Six hours remaining reminder
        elif time_step == timedelta(hours=6):
            send_notifications_for_poll(context, session, poll, 'notification.six_hours')
            poll.next_notification = poll.due_date

        # Send the closed notification, remove all notifications and close the poll
        elif poll.due_date == poll.next_notification:
            poll.closed = True
            update_poll_messages(session, context.bot, poll)

            send_notifications_for_poll(context, session, poll, 'notification.closed')
            for notification in poll.notifications:
                session.delete(notification)

        session.commit()


def send_notifications_for_poll(context, session, poll, message_key):
    """Send the notifications for a single poll depending on the remaining time."""
    locale = poll.locale
    for notification in poll.notifications:
        try:
            # Get the chat and send the notification
            tg_chat = context.bot.get_chat(notification.chat_id)
            tg_chat.send_message(
                i18n.t(message_key, locale=locale, name=poll.name),
                parse_mode='markdown',
                reply_to_message_id=notification.poll_message_id,
            )

        except BadRequest as e:
            if e.message == 'Chat not found':
                session.delete(notification)
        # Bot was removed from group
        except Unauthorized:
            session.delete(notification)


@run_async
@job_session_wrapper()
def delete_old_updates(context, session):
    """Delete all unneded updates."""
    now = datetime.now()
    time_window = now - timedelta(seconds=now.second % window_size, microseconds=now.microsecond)
    ten_minutes_ago = time_window - timedelta(days=3)

    session.query(Update) \
        .filter(Update.time_window <= ten_minutes_ago) \
        .delete()
