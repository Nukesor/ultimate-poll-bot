"""Handle messages."""
from datetime import date, datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import ObjectDeletedError, StaleDataError
from telethon.errors.rpcbaseerrors import (
    ForbiddenError,
)

from pollbot.i18n import i18n
from pollbot.client import client
from pollbot.models import Update, Poll, DailyStatistic
from pollbot.helper.session import job_wrapper
from pollbot.helper.update import send_updates, update_poll_messages


@job_wrapper(wait=2)
async def message_update_job(session):
    """Update all messages if necessary."""
    try:
        now = datetime.now()

        update_count = session.query(Update) \
            .filter(Update.next_update <= now) \
            .count()

        while update_count > 0:
            updates = session.query(Update) \
                .filter(Update.next_update <= now) \
                .options(joinedload(Update.poll)) \
                .order_by(Update.next_update.asc()) \
                .limit(50) \
                .all()

            for update in updates:
                try:
                    send_updates(session, update.poll, show_warning=True)
                    session.delete(update)
                    session.commit()
                except ObjectDeletedError:
                    # The update has already been handled somewhere else.
                    # This could be either a job or a person that voted in this very moment
                    session.rollback()
                except RetryAfter as e:
                    # Schedule an update after the RetryAfter timeout + 1 second buffer
                    update.next_update = now + timedelta(seconds=int(e.retry_after) + 1)
                    try:
                        session.commit()
                    except StaleDataError:
                        # The update has already been handled somewhere else
                        session.rollback()

            # Update the count again.
            # Updates can be removed by normal operation as well
            update_count = session.query(Update) \
                .filter(Update.next_update <= now) \
                .count()

    except Exception as e:
        raise e

    finally:
        session.close()


@job_wrapper(wait=5*60)
async def send_notifications(session):
    """Notify the users about the poll being closed soon."""
    polls = session.query(Poll) \
        .filter(or_(
            Poll.next_notification <= datetime.now(),
            Poll.due_date <= datetime.now(),
        )) \
        .filter(Poll.closed.is_(False)) \
        .all()

    for poll in polls:
        time_step = poll.due_date - poll.next_notification

        if time_step == timedelta(days=7):
            send_notifications_for_poll(session, poll, 'notification.one_week')
            poll.next_notification = poll.due_date - timedelta(days=1)

        # One day remaining reminder
        elif time_step == timedelta(days=1):
            send_notifications_for_poll(session, poll, 'notification.one_day')
            poll.next_notification = poll.due_date - timedelta(hours=6)

        # Six hours remaining reminder
        elif time_step == timedelta(hours=6):
            send_notifications_for_poll(session, poll, 'notification.six_hours')
            poll.next_notification = poll.due_date

        # Send the closed notification, remove all notifications and close the poll
        elif poll.due_date <= datetime.now():
            poll.closed = True
            update_poll_messages(session, poll)

            send_notifications_for_poll(session, poll, 'notification.closed')
            for notification in poll.notifications:
                session.delete(notification)
            session.commit()



def send_notifications_for_poll(session, poll, message_key):
    """Send the notifications for a single poll depending on the remaining time."""
    locale = poll.locale
    for notification in poll.notifications:
        try:
            # Send the notification
            client.send_message(
                notification.chat_id,
                i18n.t(message_key, locale=locale, name=poll.name),
                reply_to=notification.poll_message_id,
            )

#        except BadRequest as e:
#            if e.message == 'Chat not found':
#                session.delete(notification)
        # Bot was removed from group
        except ForbiddenError:
            session.delete(notification)


@job_wrapper(wait=6*60*60)
async def create_daily_stats(session):
    """Create the daily stats entity for today and tomorrow."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    for stat_date in [today, tomorrow]:
        statistic = session.query(DailyStatistic).get(stat_date)

        if statistic is None:
            statistic = DailyStatistic(stat_date)
            session.add(statistic)
            session.commit()
