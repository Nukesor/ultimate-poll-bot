"""The sqlalchemy model for a statistics."""
from sqlalchemy import Column, Date
from sqlalchemy.types import Integer

from pollbot.db import base


class DailyStatistic(base):
    """Daily activities all accross the bot."""

    __tablename__ = "daily_statistic"

    date = Column(Date, primary_key=True)

    votes = Column(Integer, default=0, nullable=False)
    callback_calls = Column(Integer, default=0, nullable=False)
    new_users = Column(Integer, default=0, nullable=False)
    created_polls = Column(Integer, default=0, nullable=False)
    externally_shared = Column(Integer, default=0, nullable=False)
    show_results = Column(Integer, default=0, nullable=False)
    notifications = Column(Integer, default=0, nullable=False)

    def __init__(self, date):
        """Create a new dialy statistic."""
        self.date = date
