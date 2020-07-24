"""Poll related commands."""
from typing import Optional

from telegram.ext import run_async

from pollbot.display.misc import get_poll_list
from pollbot.telegram.session import message_wrapper
from pollbot.poll.creation import initialize_poll
from pollbot.i18n import i18n
from pollbot.models import Poll


@run_async
@message_wrapper(private=True)
def create_poll(bot, update, session, user):
    """Create a new poll."""
    initialize_poll(session, user, update.message.chat)


@run_async
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


@run_async
@message_wrapper(private=True)
def list_polls(bot, update, session, user):
    """Get a list of all active polls."""
    text, keyboard = get_poll_list(session, user, 0)
    update.message.chat.send_message(text, reply_markup=keyboard)


@run_async
@message_wrapper(private=True)
def list_closed_polls(bot, update, session, user):
    """Get a list of all closed polls."""
    text, keyboard = get_poll_list(session, user, 0, closed=True)
    update.message.chat.send_message(text, reply_markup=keyboard)
