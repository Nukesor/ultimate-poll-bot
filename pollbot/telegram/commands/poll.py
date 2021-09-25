"""Poll related commands."""
from typing import Optional

from sqlalchemy.orm.scoping import scoped_session
from telegram.bot import Bot
from telegram.update import Update

from pollbot.display.misc import get_poll_list
from pollbot.i18n import i18n
from pollbot.models import Poll
from pollbot.models.user import User
from pollbot.poll.creation import initialize_poll
from pollbot.telegram.session import message_wrapper


@message_wrapper(private=True)
def create_poll(bot: Bot, update: Update, session: scoped_session, user: User) -> None:
    """Create a new poll."""
    initialize_poll(session, user, update.message.chat)


@message_wrapper(private=True)
def cancel_poll_creation(bot, update, session, user):
    """Cancels the creation of the current poll."""
    current_poll: Optional[Poll] = user.current_poll

    if current_poll is None:
        update.message.chat.send_message(
            i18n.t("delete.doesnt_exist", locale=user.locale),
        )
        return

    session.delete(current_poll)
    session.commit()
    update.effective_chat.send_message(
        f"{i18n.t('delete.previous_deleted', locale=user.locale)} /start"
    )


@message_wrapper(private=True)
def list_polls(bot: Bot, update: Update, session: scoped_session, user: User) -> None:
    """Get a list of all active polls."""
    text, keyboard = get_poll_list(session, user, 0)
    update.message.chat.send_message(text, reply_markup=keyboard)


@message_wrapper(private=True)
def list_closed_polls(
    bot: Bot, update: Update, session: scoped_session, user: User
) -> None:
    """Get a list of all closed polls."""
    text, keyboard = get_poll_list(session, user, 0, closed=True)
    update.message.chat.send_message(text, reply_markup=keyboard)
