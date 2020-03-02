"""The sqlalchemy model for a vote."""
from sqlalchemy import (
    Column,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.types import (
    DateTime,
    Integer,
)
from sqlalchemy.orm import relationship

from pollbot.db import base


class Update(base):
    """The model for a Update."""

    __tablename__ = 'update'
    __table_args__ = (
        UniqueConstraint('poll_id', name='one_update_per_poll'),
    )

    id = Column(Integer, primary_key=True)
    next_update = Column(DateTime, nullable=False)

    poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade'),
                     nullable=False, index=True)
    poll = relationship('Poll')

    def __init__(self, poll, next_update):
        """Create a new vote."""
        self.poll = poll
        self.next_update = next_update
        self.count = 0
