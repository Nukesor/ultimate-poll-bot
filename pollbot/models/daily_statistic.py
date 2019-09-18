"""The sqlalchemy model for a statistics."""
from sqlalchemy import (
    Column,
    Date,
    func,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.types import (
    Boolean,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from pollbot.db import base


class DailyStatistic(base):
    """The model for a Update."""

    __tablename__ = 'daily_statistic'

    date = Column(Date, primary_key=True)

    votes = Column(Integer, default=0, nullable=False)
    callback_calls = Column(Integer, default=0, nullable=False)
    new_users = Column(Integer, default=0, nullable=False)
    created_polls = Column(Integer, default=0, nullable=False)
    externally_shared = Column(Integer, default=0, nullable=False, server_default='0')
    show_results = Column(Integer, default=0, nullable=False, server_default='0')

    def __init__(self, date):
        """Create a new dialy statistic."""
        self.date = date
