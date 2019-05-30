"""The sqlalchemy model for a polloption."""
from sqlalchemy import (
    Column,
    func,
    ForeignKey,
)
from sqlalchemy.types import (
    Integer,
    DateTime,
    String,
)
from sqlalchemy.orm import relationship

from pollbot.db import base


class PollOption(base):
    """The model for a PollOption."""

    __tablename__ = 'poll_option'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ManyToOne
    poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade'), nullable=False, index=True)
    poll = relationship('Poll', lazy='joined')

    # OneToMany
    votes = relationship('Vote', lazy='joined')

    def __init__(self, poll, name):
        """Create a new poll."""
        self.poll = poll
        self.name = name
