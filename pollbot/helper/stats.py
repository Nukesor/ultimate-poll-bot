"""Statistics handler."""
from datetime import date, timedelta


def increase_stat(session, name):
    """Increase a specific statistic."""
    from pollbot.models import DailyStatistic
    if name == 'votes':
        column = DailyStatistic.votes
    elif name == 'callback_calls':
        column = DailyStatistic.callback_calls
    elif name == 'new_users':
        column = DailyStatistic.new_users
    elif name == 'created_polls':
        column = DailyStatistic.created_polls

    session.query(DailyStatistic) \
        .filter(DailyStatistic.date == date.today()) \
        .update({name: column + 1})
