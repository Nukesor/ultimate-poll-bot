"""Handle messages."""
from datetime import date, datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.orm.exc import ObjectDeletedError, StaleDataError
from sqlalchemy.orm.scoping import scoped_session
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.ext.callbackcontext import CallbackContext

from pollbot.config import config
from pollbot.enums import PollDeletionMode
from pollbot.i18n import i18n
from pollbot.models import DailyStatistic, Poll, Update, UserStatistic, Vote
from pollbot.poll.delete import delete_poll
from pollbot.poll.update import send_updates, update_poll_messages
from pollbot.sentry import sentry
from pollbot.telegram.session import job_wrapper


@job_wrapper
def message_update_job(context: CallbackContext, session: scoped_session) -> None:
    """Update all polls that are scheduled for an update."""
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
                    send_updates(session, context.bot, update.poll)
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
        sentry.capture_job_exception(e)

    finally:
        context.job.enabled = True


@job_wrapper
def delete_polls(context: CallbackContext, session: scoped_session) -> None:
    """Delete polls from the database and their messages if requested."""
    try:
        context.job.enabled = False

        # Only delete a few polls at a time to prevent RAM usage spikes
        polls_to_delete = (
            session.query(Poll)
            .filter(Poll.delete.isnot(None))
            .order_by(Poll.updated_at.asc())
            .limit(20)
            .all()
        )
        for poll in polls_to_delete:
            if poll.delete == PollDeletionMode.DB_ONLY.name:
                delete_poll(session, context, poll)
            elif poll.delete == PollDeletionMode.WITH_MESSAGES.name:
                delete_poll(session, context, poll, True)
            session.commit()

    except Exception as e:
        sentry.capture_job_exception(e)

    finally:
        context.job.enabled = True


@job_wrapper
def send_notifications(context: CallbackContext, session: scoped_session) -> None:
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


def send_notifications_for_poll(
    context: CallbackContext, session: scoped_session, poll: Poll, message_key: str
) -> None:
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

        except Exception as e:
            sentry.capture_job_exception(e)


@job_wrapper
def create_daily_stats(context: CallbackContext, session: scoped_session) -> None:
    """Create the daily stats entity for today and tomorrow."""
    try:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        for stat_date in [today, tomorrow]:
            statistic = session.query(DailyStatistic).get(stat_date)

            if statistic is None:
                statistic = DailyStatistic(stat_date)
                session.add(statistic)

        session.commit()
    except Exception as e:
        sentry.capture_job_exception(e)


@job_wrapper
def perma_ban_checker(context: CallbackContext, session: scoped_session) -> None:
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


@job_wrapper
def cleanup(context: CallbackContext, session: scoped_session) -> None:
    """Run various database cleanup operations."""
    user_statistics_cleanup(context, session)
    old_closed_poll_cleanup(context, session)
    old_open_poll_cleanup(context, session)
    unfinished_polls_cleanup(context, session)


def user_statistics_cleanup(context: CallbackContext, session: scoped_session) -> None:
    """Remove all user statistics after 7 days."""
    threshold = date.today() - timedelta(days=7)
    session.query(UserStatistic).filter(UserStatistic.date < threshold).delete()


def old_closed_poll_cleanup(context: CallbackContext, session: scoped_session) -> None:
    """Remove old closed polls."""
    last_update_threshold = date.today() - timedelta(days=180)

    # Subquery to check if any newer votes exist.
    poll_alias = aliased(Poll)
    newer_votes_exist_subquery = (
        session.query(Vote)
        .filter(Vote.poll_id == poll_alias.id)
        .filter(Vote.updated_at > last_update_threshold)
        .exists()
    )

    poll_ids = (
        session.query(poll_alias.id)
        .filter(poll_alias.closed.is_(True))
        .filter(poll_alias.delete.is_(None))
        .filter(poll_alias.updated_at < last_update_threshold)
        .filter(~newer_votes_exist_subquery)
        .limit(10000)
        .all()
    )

    poll_ids = [value[0] for value in poll_ids]
    session.query(Poll).filter(Poll.id.in_(poll_ids)).update(
        {"delete": PollDeletionMode.DB_ONLY.name}, synchronize_session=False
    )

    session.commit()


def old_open_poll_cleanup(context: CallbackContext, session: scoped_session) -> None:
    """Remove old open polls that haven't been touched for for a long time."""
    last_update_threshold = date.today() - timedelta(days=360)

    # Subquery to check if any newer votes exist.
    poll_alias = aliased(Poll)
    newer_votes_exist_subquery = (
        session.query(Vote)
        .filter(Vote.poll_id == poll_alias.id)
        .filter(Vote.updated_at > last_update_threshold)
        .exists()
    )

    poll_ids = (
        session.query(poll_alias.id)
        .filter(poll_alias.closed.is_(False))
        .filter(poll_alias.delete.is_(None))
        .filter(poll_alias.updated_at < last_update_threshold)
        .filter(~newer_votes_exist_subquery)
        .limit(10000)
        .all()
    )

    poll_ids = [value[0] for value in poll_ids]
    session.query(Poll).filter(Poll.id.in_(poll_ids)).update(
        {"delete": PollDeletionMode.DB_ONLY.name}, synchronize_session=False
    )

    session.commit()


def unfinished_polls_cleanup(context: CallbackContext, session: scoped_session) -> None:
    """Remove unfinished polls that haven't been touched for some time."""
    last_update_threshold = date.today() - timedelta(days=30)

    (
        session.query(Poll)
        .filter(Poll.created.is_(False))
        .filter(Poll.updated_at < last_update_threshold)
        .update({"delete": PollDeletionMode.DB_ONLY.name}, synchronize_session=False)
    )

    session.commit()
