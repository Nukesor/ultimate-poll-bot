"""Statistics handler."""
from datetime import date

from sqlalchemy.orm.scoping import scoped_session

from pollbot.models.user import User


def increase_stat(session: scoped_session, name: str) -> None:
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


def increase_user_stat(session: scoped_session, user: User, name: str) -> None:
    """Increase a specific statistic."""
    from pollbot.models import UserStatistic

    mapping = {
        "callback_calls": UserStatistic.callback_calls,
        "votes": UserStatistic.votes,
        "poll_callback_calls": UserStatistic.poll_callback_calls,
        "created_polls": UserStatistic.created_polls,
        "inline_shares": UserStatistic.inline_shares,
    }

    column = mapping[name]
    session.query(UserStatistic).filter(UserStatistic.user == user).filter(
        UserStatistic.date == date.today()
    ).update({name: column + 1})
