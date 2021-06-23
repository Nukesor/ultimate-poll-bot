"""The sqlalchemy model for a user statistics."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Column, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, Integer

from pollbot.db import base


class UserStatistic(base):
    """Statistics for user activity.

    We need to track at least some user activity, since there seem to be some users which
    abuse the bot by creating polls and spamming up to 1 million votes per day.

    I really hate doing this, but I don't see another way to prevent user-specific DOS attacks
    without tracking at least some numbers.
    """

    __tablename__ = "user_statistic"

    date = Column(Date, primary_key=True)

    callback_calls = Column(Integer, default=0, nullable=False)
    votes = Column(Integer, default=0, nullable=False)
    poll_callback_calls = Column(Integer, default=0, nullable=False)
    created_polls = Column(Integer, default=0, nullable=False)
    inline_shares = Column(Integer, default=0, nullable=False)

    # OneToOne
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="cascade", name="user"),
        nullable=False,
        index=True,
        primary_key=True,
    )
    user = relationship("User", foreign_keys="UserStatistic.user_id")

    def __init__(self, user):
        """Create a new dialy statistic."""
        self.date = date.today()
        self.user = user

    def __repr__(self):
        """Print as string."""
        text = [
            f"User {self.user.username} ({self.user_id}) {self.date}:",
            f"Votes: {self.votes}",
            f"Callback calls: {self.callback_calls}",
            f"Poll callback calls: {self.poll_callback_calls}",
            f"Created polls: {self.created_polls}",
            f"Inline shares: {self.inline_shares}",
        ]

        return "\n".join(text)
