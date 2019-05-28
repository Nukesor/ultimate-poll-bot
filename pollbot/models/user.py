"""The sqlite model for a user."""
from sqlalchemy import (
    Boolean,
    Column,
    func,
    ForeignKey,
)
from sqlalchemy.types import (
    BigInteger,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from pollbot.db import base


class User(base):
    """The model for a user."""

    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    username = Column(String, unique=True)
    admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # OneToOne
    current_poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade'), index=True)
    current_poll = relationship('Poll', uselist=False, foreign_keys='User.current_poll_id', post_update=True)

    # OneToMany
    votes = relationship('Vote')
    polls = relationship('Poll', foreign_keys='Poll.user_id', back_populates='user')

    def __init__(self, user_id, username):
        """Create a new user."""
        self.id = user_id
        if username is not None:
            self.username = username.lower()

    @staticmethod
    def get_or_create(session, tg_user):
        """Get or create a new user."""
        user = session.query(User).get(tg_user.id)
        name = User.get_name_from_tg_user(tg_user)
        if not user:
            user = User(tg_user.id, tg_user.username)
            session.add(user)
            try:
                session.commit()
            # Handle parallel user addition
            except IntegrityError as e:
                session.rollback()
                user = session.query(User).get(tg_user.id)
                if user is None:
                    raise e

        # Allways update the username in case the username changed
        if tg_user.username is not None:
            user.username = tg_user.username.lower()

        user.name = name

        return user

    @staticmethod
    def get_name_from_tg_user(tg_user):
        """Return the best possible name for a User."""
        name = ''
        if tg_user.first_name is not None:
            name = tg_user.first_name
            name += ' '
        if tg_user.last_name is not None:
            name += tg_user.last_name

        if tg_user.username is not None and name == '':
            name = tg_user.username

        return name.strip()
