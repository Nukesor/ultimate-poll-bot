"""The sqlalchemy model for a polloption."""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, DateTime, Integer, String

from pollbot.db import base
from pollbot.enums import ReferenceType


class Reference(base):
    """The model for a Reference."""

    __tablename__ = "reference"
    __mapper_args__ = {"confirm_deleted_rows": False}

    id = Column(Integer, primary_key=True)
    type = Column(String)
    bot_inline_message_id = Column(String)
    message_id = Column(BigInteger)

    # Keep those for now, in case we migrate to mtproto
    message_dc_id = Column(BigInteger)
    message_access_hash = Column(BigInteger)

    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="cascade", name="user_fk"),
        nullable=True,
        index=True,
    )
    user = relationship("User", foreign_keys="Reference.user_id")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ManyToOne
    poll_id = Column(
        Integer,
        ForeignKey("poll.id", ondelete="cascade", name="reference_poll"),
        nullable=False,
        index=True,
    )
    poll = relationship("Poll", back_populates="references")

    def __init__(
        self,
        poll,
        reference_type,
        user=None,
        message_id=None,
        inline_message_id=None,
    ):
        """Create a new poll."""
        self.poll = poll
        self.type = reference_type
        # There are three types of references
        # 1. Messages in private chat:
        # - Admin interface
        # - Private vote
        if (
            user is not None
            and message_id is not None
            and reference_type
            in [ReferenceType.admin.name, ReferenceType.private_vote.name]
        ):
            self.user = user
            self.message_id = message_id

        # 2. Messages shared via inline query
        elif (
            inline_message_id is not None
            and reference_type == ReferenceType.inline.name
        ):
            self.bot_inline_message_id = inline_message_id

        else:
            raise Exception(
                "Tried to create Reference with wrong type or missing parameters"
            )

    def __repr__(self):
        """Print as string."""
        if self.type == ReferenceType.inline.name:
            message = f"Reference {self.id}: message_id {self.message_id}"
        elif self.type == ReferenceType.admin.name:
            message = f"Reference {self.id}: message_id {self.message_id}, admin: {self.user.id}"
        else:
            message = f"Reference {self.id}: message_id {self.message_id}, user: {self.user.id}"

        return message


Index(
    "ix_unique_admin_reference",
    Reference.poll_id,
    Reference.user_id,
    Reference.message_id,
    unique=True,
    postgresql_where=Reference.type == "admin",
)

Index(
    "ix_unique_private_vote_reference",
    Reference.poll_id,
    Reference.user_id,
    Reference.message_id,
    unique=True,
    postgresql_where=Reference.type == "private_vote",
)


Index(
    "ix_unique_inline_share",
    Reference.poll_id,
    Reference.bot_inline_message_id,
    unique=True,
    postgresql_where=Reference.type == "inline",
)
