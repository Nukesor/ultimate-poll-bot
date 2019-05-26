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

        return user
