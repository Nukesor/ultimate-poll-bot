"""The sqlalchemy model for a poll."""
import random
from datetime import datetime, timedelta
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
from pollbot.helper.enums import PollType, UserSorting, OptionSorting, ExpectedInput


class Poll(base):
    """The model for a Poll."""

    __tablename__ = 'poll'

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, server_default=text('gen_random_uuid()'))

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Options
    name = Column(String)
    description = Column(String)
    locale = Column(String, default='English')
    poll_type = Column(String, nullable=False)
    number_of_votes = Column(Integer)

    # Functionality
    anonymous = Column(Boolean, nullable=False)
    results_visible = Column(Boolean, nullable=False, default=True)
    due_date = Column(DateTime, nullable=True)
    next_notification = Column(DateTime, nullable=True)
    allow_new_options = Column(Boolean, nullable=False, default=False)

    # Styling
    show_percentage = Column(Boolean, nullable=False, default=True)
    show_option_votes = Column(Boolean, nullable=False, default=True, server_default="true")
    european_date_format = Column(Boolean, nullable=False, default=False)
    permanently_summarized = Column(Boolean, nullable=False, default=False)
    compact_buttons = Column(Boolean, nullable=False, default=False)
    summarize = Column(Boolean, nullable=False, default=False)
    option_sorting = Column(String, nullable=False)
    user_sorting = Column(String, nullable=False)

    # Flags
    created = Column(Boolean, nullable=False, default=False)
    closed = Column(Boolean, nullable=False, default=False)

    # Chat state variables
    expected_input = Column(String)
    in_settings = Column(Boolean, nullable=False, default=False)
    current_date = Column(Date, server_default=func.now(), nullable=False)

    # OneToOne
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='cascade', name='user'), nullable=False, index=True)
    user = relationship('User', foreign_keys='Poll.user_id')

    # OneToMany
    options = relationship('PollOption', order_by='asc(PollOption.id)', lazy='joined', passive_deletes='all')
    votes = relationship('Vote', passive_deletes='all')
    references = relationship('Reference', lazy='joined', passive_deletes='all')
    notifications = relationship('Notification', passive_deletes='all')

    def __init__(self, user):
        """Create a new poll."""
        self.user = user
        self.poll_type = PollType.single_vote.name
        self.anonymous = False
        self.results_visible = True

        self.user_sorting = UserSorting.user_chrono.name
        self.option_sorting = OptionSorting.option_chrono.name

    @staticmethod
    def create(user, session):
        """Create a poll from a user."""
        poll = Poll(user)
        poll.european_date_format = user.european_date_format
        poll.locale = user.locale
        user.current_poll = poll
        user.expected_input = ExpectedInput.name.name
        session.add(poll)
        session.commit()

        return poll

    def __repr__(self):
        """Print as string."""
        return f'Poll with Id: {self.id}, name: {self.name}, locale: {self.locale}'

    def should_show_result(self):
        """Determine, whether this results of this poll should be shown."""
        return self.results_visible or self.closed

    def is_doodle(self):
        return self.poll_type == PollType.doodle.name

    def is_stv(self):
        return self.poll_type == PollType.single_transferable_vote.name

    def has_date_option(self):
        """Check whether this poll has a date option."""
        for option in self.options:
            if option.is_date:
                return True
        return False

    def get_formatted_due_date(self):
        """Get the formatted date."""
        if self.european_date_format:
            return self.due_date.strftime('%d.%m.%Y %H:%M UTC')

        return self.due_date.strftime('%Y-%m-%d %H:%M UTC')

    def set_due_date(self, date):
        """Set the due date and the next notification."""
        if date is None:
            self.due_date = None
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

    def clone(self, session):
        """Create a clone from the current poll."""
        poll = Poll(self.user)
        poll.created = True
        session.add(poll)

        poll.name = self.name
        poll.description = self.description
        poll.poll_type = self.poll_type
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
            new_option.description = option.description
            new_option.is_date = option.is_date
            session.add(new_option)

        return poll

    def init_votes_for_new_options(self, session):
        """
        When a new option is added, we need to create new votes
        for all users that have already voted for this poll
        """
        assert self.is_stv()

        from pollbot.models import User, Vote, PollOption
        users = session.query(User) \
            .join(User.votes) \
            .filter(Vote.poll == self) \
            .all()

        new_options = session.query(PollOption) \
            .filter(PollOption.poll == self) \
            .outerjoin(Vote) \
            .filter(Vote.id == None) \
            .all()

        existing_options_count = len(self.options) - len(new_options)

        for user in users:
            for index, option in enumerate(new_options):
                print(option)
                vote = Vote(user, option)
                vote.priority = existing_options_count + index
                user.votes.append(vote)

    def init_votes(self, session, user):
        """
        Since STV votes always need priorities, call this to create a vote
        for every option in the poll with a random priority for the given user
        """
        assert self.is_stv()

        print('init votes')

        from pollbot.models import Vote

        votes_exist = session.query(Vote) \
            .filter(Vote.user == user) \
            .filter(Vote.poll == self) \
            .first() is not None

        if votes_exist:
            print('votes exist')
            return

        votes = []
        for index, option in enumerate(random.sample(self.options, len(self.options))):
            vote = Vote(user, option)
            vote.priority = index
            votes.append(vote)
        session.add_all(votes)

