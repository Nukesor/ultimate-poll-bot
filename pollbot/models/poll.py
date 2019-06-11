"""The sqlalchemy model for a poll."""
from sqlalchemy import (
    Date,
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
from pollbot.helper.enums import VoteType, UserSorting, OptionSorting


class Poll(base):
    """The model for a Poll."""

    __tablename__ = 'poll'
    __table_args__ = (
    )

    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Options
    name = Column(String)
    description = Column(String)
    vote_type = Column(String, nullable=False)
    anonymous = Column(Boolean, nullable=False)
    number_of_votes = Column(Integer)
    option_sorting = Column(String, nullable=False)
    user_sorting = Column(String, nullable=False)
    results_visible = Column(Boolean, nullable=False, default=True)
    show_percentage = Column(Boolean, nullable=False, default=True, server_default='true')

    # Flags
    created = Column(Boolean, default=False, nullable=False)
    closed = Column(Boolean, default=False, nullable=False)

    # Chat state variables
    expected_input = Column(String)
    in_settings = Column(Boolean, default=False, nullable=False)
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
        self.expected_input = 'name'
        self.anonymous = False
        self.results_visible = True

        self.user_sorting = UserSorting.user_chrono.name
        self.option_sorting = OptionSorting.option_chrono.name

    def should_show_result(self):
        """Determine, whether this results of this poll should be shown."""
        return self.results_visible or self.closed
