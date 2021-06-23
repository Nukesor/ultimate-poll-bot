"""The sqlite model for a user."""
from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, DateTime, String

from pollbot.db import base


class User(base):
    """The model for a user."""

    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    username = Column(String)

    # Flags
    started = Column(Boolean, nullable=False, default=False)
    banned = Column(Boolean, nullable=False, default=False)
    broadcast_sent = Column(Boolean, nullable=False, default=False)
    last_update = Column(DateTime)

    # Debug time j
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Permanent settings
    admin = Column(Boolean, nullable=False, default=False)
    locale = Column(String, default="English")
    european_date_format = Column(Boolean, nullable=False, default=False)
    notifications_enabled = Column(Boolean, nullable=False, default=True)

    # Chat logic
    expected_input = Column(String)

    # Simple foreign key
    current_poll_id = Column(
        BigInteger,
        ForeignKey("poll.id", ondelete="set null", name="current_poll"),
        index=True,
    )
    current_poll = relationship(
        "Poll", uselist=False, foreign_keys="User.current_poll_id", post_update=True
    )

    # OneToMany
    votes = relationship("Vote")
    polls = relationship("Poll", foreign_keys="Poll.user_id", back_populates="user")

    def __init__(self, user_id, username):
        """Create a new user."""
        self.id = user_id
        if username is not None:
            self.username = username.lower()

    def __repr__(self):
        """Print as string."""
        return f"User with Id: {self.id}, name: {self.name}, locale: {self.locale}"

    def delete(self):
        """Delete the user."""
        self.started = False
        self.current_poll = None
        self.username = "GDPR removed user"
        self.name = "GDPR removed user"
        self.locale = "English"
        self.european_date_format = False
        self.notifications_enabled = False
