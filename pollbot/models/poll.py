"""The sqlalchemy model for a poll."""
from datetime import date
from sqlalchemy import (
    Date,
    Column,
    func,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from pollbot.db import base
from pollbot.helper.enums import VoteType, UserSorting, OptionSorting


class Poll(base):
    """The model for a Poll."""

    __tablename__ = 'poll'
    __table_args__ = (
    )

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, server_default=text('gen_random_uuid()'))

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Options
    name = Column(String)
    description = Column(String)
    vote_type = Column(String, nullable=False)
    anonymous = Column(Boolean, nullable=False)
    number_of_votes = Column(Integer)
    allow_new_options = Column(Boolean, nullable=False, default=False)
    option_sorting = Column(String, nullable=False)
    user_sorting = Column(String, nullable=False)
    results_visible = Column(Boolean, nullable=False, default=True)
    show_percentage = Column(Boolean, nullable=False, default=True)
    european_date_format = Column(Boolean, nullable=False, default=False)

    # Flags
    created = Column(Boolean, nullable=False, default=False)
    closed = Column(Boolean, nullable=False, default=False)
    deleted = Column(Boolean, nullable=False, default=False)
    due_date = Column(Date, nullable=True)

    # Chat state variables
    expected_input = Column(String)
    in_settings = Column(Boolean, nullable=False, default=False)
    current_date = Column(Date, server_default=func.now(), nullable=False)

    # OneToOne
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='cascade'), nullable=False, index=True)
    user = relationship('User', foreign_keys='Poll.user_id')

    # OneToMany
    options = relationship('PollOption', order_by='asc(PollOption.id)', lazy='joined', passive_deletes='all')
    votes = relationship('Vote', passive_deletes=True)
    references = relationship('Reference', lazy='joined', passive_deletes='all')

    def __init__(self, user):
        """Create a new poll."""
        self.user = user
        self.vote_type = VoteType.single_vote.name
        self.anonymous = False
        self.results_visible = True

        self.user_sorting = UserSorting.user_chrono.name
        self.option_sorting = OptionSorting.option_chrono.name

    def __repr__(self):
        """Print as string."""
        return f'Poll with Id: {self.id}, name: {self.name}'

    def __str__(self):
        """Print as string."""
        return f'Poll with Id: {self.id}, name: {self.name}'

    def should_show_result(self):
        """Determine, whether this results of this poll should be shown."""
        return self.results_visible or self.closed

    def has_date_option(self):
        """Check whether this poll has a date option."""
        for option in self.options:
            if option.is_date:
                return True
        return False

    def get_formatted_due_date(self):
        """Get the formatted date."""
        if self.european_date_format:
            return self.due_date.strftime('%d.%m.%Y')

        return self.due_date.isoformat()

    def clone(self, session):
        """Create a clone from the current poll."""
        poll = Poll(self.user)
        poll.created = True
        session.add(poll)

        poll.name = self.name
        poll.description = self.description
        poll.vote_type = self.vote_type
        poll.anonymous = self.anonymous
        poll.number_of_votes = self.number_of_votes
        poll.allow_new_options = self.allow_new_options
        poll.option_sorting = self.option_sorting
        poll.user_sorting = self.user_sorting
        poll.results_visible = self.results_visible
        poll.show_percentage = self.show_percentage

        from pollbot.models import PollOption
        for option in self.options:
            new_option = PollOption(poll, option.name)
            session.add(new_option)

        return poll
