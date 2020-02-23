"""The sqlalchemy model for a polloption."""
from sqlalchemy import (
    Column,
    func,
    ForeignKey,
)
from sqlalchemy.types import (
    BigInteger,
    Integer,
    DateTime,
    String,
)
from sqlalchemy.orm import relationship

from pollbot.db import base


class Reference(base):
    """The model for a Reference."""

    __tablename__ = 'reference'

    id = Column(Integer, primary_key=True)
    legacy_inline_message_id = Column(String)
    inline_message_id = Column(BigInteger)
    inline_message_dc_id = Column(BigInteger)
    inline_message_access_hash = Column(BigInteger)

    admin_message_id = Column(BigInteger)
    admin_user_id = Column(BigInteger, ForeignKey('user.id', ondelete='cascade', name='admin_user'), nullable=True, index=True)
    admin_user = relationship('User', foreign_keys='Reference.admin_user_id')

    vote_message_id = Column(BigInteger)
    vote_user_id = Column(BigInteger, ForeignKey('user.id', ondelete='cascade', name='vote_user'), nullable=True, index=True)
    vote_user = relationship('User', foreign_keys='Reference.vote_user_id')

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ManyToOne
    poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade', name="reference_poll"), nullable=False, index=True)
    poll = relationship('Poll')

    def __init__(
        self, poll,
        inline_message_id=None,
        inline_message_dc_id=None,
        inline_message_access_hash=None,
        admin_user=None,
        admin_message_id=None,
        vote_user=None,
        vote_message_id=None
    ):
        """Create a new poll."""
        self.poll = poll
        self.inline_message_id = inline_message_id
        self.inline_message_dc_id = inline_message_dc_id
        self.inline_message_access_hash = inline_message_access_hash
        self.admin_user = admin_user
        self.admin_message_id = admin_message_id
        self.vote_user = vote_user
        self.vote_message_id = vote_message_id

    def __repr__(self):
        """Print as string."""
        if self.inline_message_id is not None:
            message = f'Reference {self.id}: inline_message_id {self.inline_message_id}'
        elif self.admin_user is not None:
            message = f'Reference {self.id}: admin_message_id {self.admin_message_id}'
            message += f', admin_id: {self.admin_user.id}'
        else:
            message = f'Reference {self.id}: vote_message_id {self.vote_message_id}'
            message += f', vote_user_id : {self.vote_user.id}'

        return message
