"""The sqlalchemy model for a vote."""
from sqlalchemy import (
    Column,
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


class Update(base):
    """The model for a Update."""

    __tablename__ = 'update'
    __table_args__ = (
        UniqueConstraint('poll_id', 'time_window', name='one_update_per_time_window'),
    )

    id = Column(Integer, primary_key=True)
    poll_id = Column(String)

    count = Column(Integer, nullable=False)
    updated = Column(Boolean, default=False, nullable=False)
    time_window = Column(DateTime, nullable=False)

    poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade'), nullable=False, index=True)
    poll = relationship('Poll')

    def __init__(self, poll, time_window):
        """Create a new vote."""
        self.poll = poll
        self.time_window = time_window
        self.count = 0
