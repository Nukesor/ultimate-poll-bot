"""The sqlalchemy model for a vote."""
from sqlalchemy import (
    Column,
    func,
    ForeignKey,
    Index,
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


class Vote(base):
    """The model for a Vote."""

    __tablename__ = 'vote'
    __table_args__ = (
        UniqueConstraint('user_id', 'poll_id', 'poll_option_id',
                         name='one_vote_per_option_and_user'),
    )

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=True)
    priority = Column(Integer, nullable=True)
    poll_type = Column(String, nullable=True)
    vote_count = Column(Integer)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ManyToOne
    poll_option_id = Column(Integer, ForeignKey('poll_option.id', ondelete='cascade'), nullable=False, index=True)
    poll_option = relationship('PollOption')

    poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade'), nullable=False, index=True)
    poll = relationship('Poll')

    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='cascade'), nullable=False, index=True)
    user = relationship('User')

    def __init__(self, user, poll_option):
        """Create a new vote."""
        self.user = user
        self.vote_count = 1
        self.poll_option = poll_option
        self.poll = poll_option.poll
        self.poll_type = self.poll.poll_type

    def __repr__(self):
        """Print as string."""
        return f'Vote with Id: {self.id}, poll: {self.poll_id}'


Index(
    'ix_unique_single_vote',
    Vote.user_id, Vote.poll_id,
    unique=True,
    postgresql_where=Vote.poll_type == 'single_vote',
)
