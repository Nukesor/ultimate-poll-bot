"""The sqlalchemy model for a poll."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import Column, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.types import BigInteger, Boolean, DateTime, Integer, String

from pollbot.db import base
from pollbot.enums import ExpectedInput, OptionSorting, PollType, UserSorting
from pollbot.models.option import Option
from pollbot.models.user import User


class Poll(base):
    """The model for a Poll."""

    __tablename__ = "poll"

    id = Column(Integer, primary_key=True)
    uuid = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
    )

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Options
    name = Column(String)
    description = Column(String)
    locale = Column(String, default="English")
    poll_type = Column(String, nullable=False)
    number_of_votes = Column(Integer, default=0)

    # Functionality
    anonymous = Column(Boolean, nullable=False)
    results_visible = Column(Boolean, nullable=False, default=True)
    due_date = Column(DateTime, nullable=True)
    next_notification = Column(DateTime, nullable=True)
    allow_new_options = Column(Boolean, nullable=False, default=False)
    allow_sharing = Column(Boolean, nullable=False, default=False)

    # Styling
    show_percentage = Column(Boolean, nullable=False, default=True)
    show_option_votes = Column(Boolean, nullable=False, default=True)
    european_date_format = Column(Boolean, nullable=False, default=False)
    permanently_summarized = Column(Boolean, nullable=False, default=False)
    compact_buttons = Column(Boolean, nullable=False, default=False)
    summarize = Column(Boolean, nullable=False, default=False)
    option_sorting = Column(String, nullable=False)
    user_sorting = Column(String, nullable=False)

    # Flags
    created = Column(Boolean, nullable=False, default=False)
    closed = Column(Boolean, nullable=False, default=False)
    # Set this, if the poll should be deleted.
    # There are two modes: DB_ONLY and WITH_MESSAGES.
    delete = Column(String)

    # Chat state variables
    expected_input = Column(String)
    in_settings = Column(Boolean, nullable=False, default=False)
    created_from_native = Column(
        Boolean, nullable=False, server_default="False", default=False
    )

    # ManyToOne
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="cascade", name="user"),
        nullable=False,
        index=True,
    )
    user = relationship("User", foreign_keys="Poll.user_id")

    # OneToMany
    options = relationship(
        "Option",
        order_by="asc(Option.index)",
        lazy="joined",
        passive_deletes="all",
        back_populates="poll",
    )
    votes = relationship("Vote", passive_deletes="all", back_populates="poll")
    references = relationship(
        "Reference", lazy="joined", passive_deletes="all", back_populates="poll"
    )
    notifications = relationship(
        "Notification", passive_deletes="all", back_populates="poll"
    )

    def __init__(self, user):
        """Create a new poll."""
        self.user = user
        self.poll_type = PollType.single_vote.name
        self.anonymous = False
        self.results_visible = True

        self.user_sorting = UserSorting.chrono.name
        self.option_sorting = OptionSorting.manual.name

    @staticmethod
    def create(user: User, session: scoped_session) -> Poll:
        """Create a poll from a user."""
        poll = Poll(user)
        poll.european_date_format = user.european_date_format
        poll.locale = user.locale
        user.current_poll = poll
        user.expected_input = ExpectedInput.name.name
        session.add(poll)
        session.flush()

        return poll

    def __repr__(self):
        """Print as string."""
        return f"Poll with Id: {self.id}, name: {self.name}, locale: {self.locale}"

    def should_show_result(self) -> bool:
        """Determine, whether this results of this poll should be shown."""
        return self.results_visible or self.closed

    def is_doodle(self) -> bool:
        return self.poll_type == PollType.doodle.name

    def is_priority(self) -> bool:
        return self.poll_type == PollType.priority.name

    def has_date_option(self) -> bool:
        """Check whether this poll has a date option."""
        for option in self.options:
            if option.is_date:
                return True
        return False

    def get_date_option(self, check_date: date) -> Optional[Option]:
        """Return whether an option with this date already exists."""
        for option in self.options:
            if option.is_date and option.as_date() == check_date:
                return option
        return None

    def get_formatted_due_date(self) -> str:
        """Get the formatted date."""
        if self.european_date_format:
            return self.due_date.strftime("%d.%m.%Y %H:%M UTC")

        return self.due_date.strftime("%Y-%m-%d %H:%M UTC")

    def set_due_date(self, date: Optional[datetime]) -> None:
        """Set the due date and the next notification."""
        if date is None:
            self.due_date = None
            self.next_notification = None
            return

        # Calculate the next_notification date depending
        # on the given due date
        now = datetime.now()
        self.due_date = date
        if now < self.due_date - timedelta(days=7):
            self.next_notification = self.due_date - timedelta(days=7)
        elif now < self.due_date - timedelta(days=1):
            self.next_notification = self.due_date - timedelta(days=1)
        elif now < self.due_date - timedelta(hours=6):
            self.next_notification = self.due_date - timedelta(hours=6)
        else:
            self.next_notification = self.due_date
