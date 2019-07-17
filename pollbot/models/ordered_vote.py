from sqlalchemy import (
    Column,
    func,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.types import (
    BigInteger,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from pollbot.db import base

class OrderedVote(base):
    __tablename__ = 'ordered_vote'
    __table_args__ = (
        UniqueConstraint('user_id', 'poll_id', 'priority',
                         name='no_duplicate_priority'),
    )

    id = Column(Integer, primary_key=True)
    priority = Column(Integer, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ManyToOne
    poll_option_id = Column(Integer, ForeignKey('poll_option.id', ondelete='cascade'), nullable=False, index=True)
    poll_option = relationship('PollOption')

    poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade'), nullable=False, index=True)
    poll = relationship('Poll')

    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='cascade'), nullable=False, index=True)
    user = relationship('User')

    def __init__(self, user, poll_option, priority):
        """Create a new ordered vote."""
        self.user = user
        self.poll_option = poll_option
        self.poll = poll_option.poll
        self.priority = priority

    def __repr__(self):
        """Print as string."""
        return f'Vote with Id: {self.id}, poll: {self.poll_id}'

    def __str__(self):
        """Print as string."""
        return f'Vote with Id: {self.id}, poll: {self.poll_id}'
