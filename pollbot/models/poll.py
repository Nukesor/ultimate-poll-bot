"""The sqlalchemy model for a poll."""
from sqlalchemy import (
    Column,
    func,
    ForeignKey,
)
from sqlalchemy.types import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from pollbot.db import base
from pollbot.helper.enums import PollType


class Poll(base):
    """The model for a Poll."""

    __tablename__ = 'poll'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    creation_step = Column(String, nullable=False)
    finished = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    name = Column(String)
    description = Column(String)

    # Options
    anonymous = Column(Boolean, nullable=False)

    # OneToOne
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='cascade'), nullable=False, index=True)
    user = relationship('User', foreign_keys='Poll.user_id', back_populates='polls')

    # OneToMany
    options = relationship('PollOption', order_by='asc(PollOption.id)')
    votes = relationship('Vote', order_by='asc(PollOption.id)')
    references = relationship('Reference')

    def __init__(self, user):
        """Create a new poll."""
        self.user = user
        self.type = PollType.single_vote.name
        self.creation_step = 'name'
        self.anonymous = True
