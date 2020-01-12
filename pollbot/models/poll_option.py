"""The sqlalchemy model for a polloption."""
from datetime import date
from sqlalchemy import (
    Column,
    func,
    ForeignKey,
)
from sqlalchemy.types import (
    Boolean,
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
    name = Column(String, nullable=False)
    description = Column(String)
    is_date = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ManyToOne
    poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade'), nullable=False, index=True)
    poll = relationship('Poll', lazy='joined')

    # OneToMany
    votes = relationship('Vote', lazy='joined', passive_deletes='all', order_by='Vote.id')

    def __init__(self, poll, name):
        """Create a new poll."""
        self.poll = poll
        self.name = name

    def __repr__(self):
        """Print as string."""
        return f'Option with Id: {self.id}, poll: {self.poll_id}, name: {self.name}'

    def get_formatted_name(self):
        """Get the name depending on whether the option is a date."""
        if self.is_date and self.poll.european_date_format:
            option_date = date.fromisoformat(self.name)
            return option_date.strftime('%d.%m.%Y (%A)')
        elif self.is_date:
            option_date = date.fromisoformat(self.name)
            return option_date.strftime('%Y-%m-%d (%A)')

        return self.name

    def as_date(self):
        """Either return the option as date or None."""
        if not self.is_date:
            return None
        return date.fromisoformat(self.name)
