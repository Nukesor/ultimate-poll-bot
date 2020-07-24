"""Handle messages."""
from datetime import date, datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from telegram.ext import run_async
from telegram.error import BadRequest, Unauthorized, RetryAfter
from sqlalchemy.orm.exc import ObjectDeletedError, StaleDataError

from pollbot.i18n import i18n
from pollbot.config import config
from pollbot.models import Update, Poll, DailyStatistic, UserStatistic
from pollbot.telegram.session import job_wrapper
from pollbot.poll.update import send_updates, update_poll_messages


@run_async
@job_wrapper
def message_update_job(context, session):
    """Update all messages if necessary."""
    try:
        context.job.enabled = False
        now = datetime.now()

        update_count = session.query(Update).filter(Update.next_update <= now).count()

        while update_count > 0:
            updates = (
                session.query(Update)
                .filter(Update.next_update <= now)
                .options(joinedload(Update.poll))
                .order_by(Update.next_update.asc())
                .limit(50)
                .all()
            )

            for update in updates:
                try:
                    send_updates(session, context.bot, update.poll, show_warning=True)
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
            update_count = (
                session.query(Update).filter(Update.next_update <= now).count()
            )

    except Exception as e:
        raise e

    finally:
        context.job.enabled = True
        session.close()


@run_async
@job_wrapper
def send_notifications(context, session):
    """Notify the users about the poll being closed soon."""
    polls = (
        session.query(Poll)
        .filter(
            or_(
                Poll.next_notification <= datetime.now(),
                Poll.due_date <= datetime.now(),
            )
        )
        .filter(Poll.closed.is_(False))
        .all()
    )

    for poll in polls:
        time_step = poll.due_date - poll.next_notification

        if time_step == timedelta(days=7):
            send_notifications_for_poll(context, session, poll, "notification.one_week")
            poll.next_notification = poll.due_date - timedelta(days=1)

        # One day remaining reminder
        elif time_step == timedelta(days=1):
            send_notifications_for_poll(context, session, poll, "notification.one_day")
            poll.next_notification = poll.due_date - timedelta(hours=6)

        # Six hours remaining reminder
        elif time_step == timedelta(hours=6):
            send_notifications_for_poll(
                context, session, poll, "notification.six_hours"
            )
            poll.next_notification = poll.due_date

        # Send the closed notification, remove all notifications and close the poll
        elif poll.due_date <= datetime.now():
            poll.closed = True
            update_poll_messages(session, context.bot, poll)

            send_notifications_for_poll(context, session, poll, "notification.closed")
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
                parse_mode="markdown",
                reply_to_message_id=notification.poll_message_id,
            )

        except BadRequest as e:
            if e.message == "Chat not found":
                session.delete(notification)
        # Bot was removed from group
        except Unauthorized:
            session.delete(notification)


@run_async
@job_wrapper
def create_daily_stats(context, session):
    """Create the daily stats entity for today and tomorrow."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    for stat_date in [today, tomorrow]:
        statistic = session.query(DailyStatistic).get(stat_date)

        if statistic is None:
            statistic = DailyStatistic(stat_date)
            session.add(statistic)
            session.commit()


@run_async
@job_wrapper
def perma_ban_checker(context, session):
    """Perma-ban people that send more than 250 votes for at least 3 days in the last week."""
    vote_limit = config["telegram"]["max_user_votes_per_day"]
    stats = (
        session.query(UserStatistic)
        .filter(UserStatistic.votes >= vote_limit)
        .filter(UserStatistic.date == date.today())
        .all()
    )

    for stat in stats:
        # Check how often the user reached the limit in the last week
        days_above_limit = (
            session.query(UserStatistic)
            .filter(UserStatistic.votes >= vote_limit)
            .filter(UserStatistic.date >= date.today() - timedelta(days=6))
            .filter(UserStatistic.date <= date.today() - timedelta(days=1))
            .filter(UserStatistic.user == stat.user)
            .all()
        )

        # If the user reached the limit on two other days in the last week (three days in total)
        if len(days_above_limit) >= 2:
            stat.user.banned = True


@run_async
@job_wrapper
def cleanup(context, session):
    """Remove all user statistics after 7 days."""
    threshold = date.today() - timedelta(days=7)
    session.query(UserStatistic).filter(UserStatistic.date < threshold).delete()
