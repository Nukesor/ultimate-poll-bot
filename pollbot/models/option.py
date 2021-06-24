"""The sqlalchemy model for a polloption."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Column, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean, DateTime, Integer, String

from pollbot.db import base


class Option(base):
    """The model for a Option."""

    __tablename__ = "option"
    __table_args__ = (
        UniqueConstraint(
            "poll_id", "index", name="unique_option_index", deferrable=True
        ),
    )

    id = Column(Integer, primary_key=True)
    index = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    is_date = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ManyToOne
    poll_id = Column(
        Integer, ForeignKey("poll.id", ondelete="cascade"), nullable=False, index=True
    )
    poll = relationship("Poll", lazy="joined", back_populates="options")

    # OneToMany
    votes = relationship(
        "Vote",
        lazy="joined",
        passive_deletes="all",
        order_by="Vote.id",
        back_populates="option",
    )

    def __init__(self, poll, name):
        """Create a new poll."""
        self.name = name
        if len(poll.options) == 0:
            self.index = 0
        else:
            self.index = max(option.index for option in poll.options) + 1
        self.poll = poll

    def __repr__(self):
        """Print as string."""
        return f"Option with Id: {self.id}, poll: {self.poll_id}, name: {self.name}"

    def get_formatted_name(self) -> str:
        """Get the name depending on whether the option is a date."""
        if self.is_date and self.poll.european_date_format:
            option_date = date.fromisoformat(self.name)
            return option_date.strftime("%d.%m.%Y (%A)")
        elif self.is_date:
            option_date = date.fromisoformat(self.name)
            return option_date.strftime("%Y-%m-%d (%A)")

        return self.name

    def as_date(self) -> Optional[date]:
        """Either return the option as date or None."""
        if not self.is_date:
            return None
        return date.fromisoformat(self.name)
