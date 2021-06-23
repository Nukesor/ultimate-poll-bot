"""The sqlalchemy model for a vote."""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, DateTime, Integer

from pollbot.db import base


class Notification(base):
    """Notifications to send reminders of soon closing polls."""

    __tablename__ = "notification"
    __table_args__ = (
        UniqueConstraint(
            "poll_id", "chat_id", name="one_notification_per_poll_and_chat"
        ),
    )

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    select_message_id = Column(BigInteger)
    poll_message_id = Column(BigInteger)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ManyToOne
    poll_id = Column(Integer, ForeignKey("poll.id", ondelete="cascade"), index=True)
    poll = relationship("Poll", lazy="joined", back_populates="notifications")

    def __init__(self, chat_id, poll_message_id=None):
        """Create a new poll."""
        self.chat_id = chat_id
        self.poll_message_id = poll_message_id
