"""Poll creation helper."""
from typing import Optional

from sqlalchemy.orm.scoping import scoped_session
from telegram.chat import Chat
from telegram.message import Message

from pollbot.config import config
from pollbot.display.creation import get_init_text
from pollbot.display.poll.compilation import get_poll_text
from pollbot.enums import ReferenceType
from pollbot.helper.stats import increase_stat, increase_user_stat
from pollbot.i18n import i18n
from pollbot.models import Poll, Reference, User
from pollbot.telegram.keyboard.creation import (
    get_cancel_creation_keyboard,
    get_init_keyboard,
)
from pollbot.telegram.keyboard.management import get_management_keyboard


def initialize_poll(session: scoped_session, user: User, chat: Chat) -> None:
    """Initialize a new poll and send the user the poll creation message.

    This function also prevents users from:
        - Having too many polls.
        - Creating a new poll, when they're already in the middle of
            creating another poll
    """
    user.started = True

    # Early return, if the user owns too many polls
    if len(user.polls) > config["telegram"]["max_polls_per_user"]:
        chat.send_message(
            i18n.t("creation.too_many_polls", locale=user.locale, count=len(user.polls))
        )
        return

    # Early return, if the user is already in the middle of creating a poll
    if user.current_poll is not None and not user.current_poll.created:
        chat.send_message(
            i18n.t("creation.already_creating", locale=user.locale),
            reply_markup=get_cancel_creation_keyboard(user.current_poll),
        )
        return

    poll = Poll.create(user, session)
    text = get_init_text(poll)
    keyboard = get_init_keyboard(poll)

    chat.send_message(
        text,
        parse_mode="markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


def create_poll(
    session: scoped_session,
    poll: Poll,
    user: User,
    chat: Chat,
    message: Optional[Message] = None,
) -> None:
    """Finish the poll creation."""
    poll.created = True
    user.expected_input = None
    user.current_poll = None

    text = get_poll_text(session, poll)

    if len(text) > 4000:
        error_message = i18n.t("misc.over_4000", locale=user.locale)
        message = chat.send_message(error_message, parse_mode="markdown")
        session.delete(poll)
        return

    if message:
        message = message.edit_text(
            text,
            parse_mode="markdown",
            reply_markup=get_management_keyboard(poll),
            disable_web_page_preview=True,
        )
    else:
        message = chat.send_message(
            text,
            parse_mode="markdown",
            reply_markup=get_management_keyboard(poll),
            disable_web_page_preview=True,
        )

    if len(text) > 3000:
        error_message = i18n.t("misc.over_3000", locale=user.locale)
        message = chat.send_message(error_message, parse_mode="markdown")

    reference = Reference(
        poll, ReferenceType.admin.name, user=user, message_id=message.message_id
    )
    session.add(reference)
    session.commit()

    increase_stat(session, "created_polls")
    increase_user_stat(session, user, "created_polls")
