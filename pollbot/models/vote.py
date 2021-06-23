"""The sqlalchemy model for a vote."""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, DateTime, Integer, String

from pollbot.db import base


class Vote(base):
    """The model for a Vote."""

    __tablename__ = "vote"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "poll_id", "option_id", name="one_vote_per_option_and_user"
        ),
    )
    __mapper_args__ = {"confirm_deleted_rows": False}

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=True)
    priority = Column(Integer, nullable=True)
    poll_type = Column(String, nullable=True)
    vote_count = Column(Integer)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ManyToOne
    option_id = Column(
        Integer,
        ForeignKey("option.id", ondelete="cascade", name="vote_option_id_fkey"),
        nullable=False,
        index=True,
    )
    option = relationship("Option", back_populates="votes")

    poll_id = Column(
        Integer, ForeignKey("poll.id", ondelete="cascade"), nullable=False, index=True
    )
    poll = relationship(
        "Poll",
        back_populates="votes",
    )

    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="cascade"),
        index=True,
    )
    user = relationship(
        "User",
        back_populates="votes",
    )

    def __init__(self, user, option):
        """Create a new vote."""
        self.user = user
        self.vote_count = 1
        self.option = option
        self.poll = option.poll
        self.poll_type = self.poll.poll_type

    def __repr__(self):
        """Print as string."""
        return f"Vote with Id: {self.id}, poll: {self.poll_id}"


Index(
    "ix_unique_single_vote",
    Vote.user_id,
    Vote.poll_id,
    unique=True,
    postgresql_where=Vote.poll_type == "single_vote",
)

Index(
    "ix_unique_priority_vote",
    Vote.user_id,
    Vote.poll_id,
    Vote.priority,
    unique=True,
    postgresql_where=Vote.poll_type == "priority",
)
