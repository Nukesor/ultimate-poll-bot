"""Statistics handler."""
from datetime import date, timedelta


def increase_stat(session, name):
    """Increase a specific statistic."""
    from pollbot.models import DailyStatistic

    mapping = {
        "votes": DailyStatistic.votes,
        "callback_calls": DailyStatistic.callback_calls,
        "new_users": DailyStatistic.new_users,
        "created_polls": DailyStatistic.created_polls,
        "externally_shared": DailyStatistic.externally_shared,
        "show_results": DailyStatistic.show_results,
        "notifications": DailyStatistic.notifications,
    }

    column = mapping[name]
    session.query(DailyStatistic).filter(DailyStatistic.date == date.today()).update(
        {name: column + 1}
    )
