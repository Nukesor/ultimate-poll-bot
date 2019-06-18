"""Handle messages."""
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

from pollbot.models import Update
from pollbot.helper.session import job_session_wrapper
from pollbot.helper.update import send_updates, window_size


@job_session_wrapper()
def message_update_job(context, session):
    """Update all messages if necessary."""
    try:
        context.job.disabled = False
        now = datetime.now()
        current_time_window = now - timedelta(seconds=now.second % window_size, microseconds=now.microsecond)
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

            # Smaller 60, because we need a liiiittle bit of buffer. Timings aren't allways perfect
            if updates_in_last_minute < 59:
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
