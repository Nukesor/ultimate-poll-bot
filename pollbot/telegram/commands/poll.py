"""Poll related commands."""
from typing import Optional

from telegram.ext import run_async

from pollbot.display.creation import get_init_text
from pollbot.display.misc import get_poll_list
from pollbot.helper.session import message_wrapper
from pollbot.i18n import i18n
from pollbot.models import Poll
from pollbot.telegram.keyboard import (
    get_cancel_creation_keyboard,
    get_init_keyboard,
)


@run_async
@message_wrapper(private=True)
def create_poll(bot, update, session, user):
    """Create a new poll."""
    # The previous unfinished poll will be removed
    user.started = True
    if user.current_poll is not None and not user.current_poll.created:
        update.message.chat.send_message(
            i18n.t("creation.already_creating", locale=user.locale),
            reply_markup=get_cancel_creation_keyboard(user.current_poll),
        )
        return

    poll = Poll.create(user, session)
    text = get_init_text(poll)
    keyboard = get_init_keyboard(poll)

    update.message.chat.send_message(
        text,
        parse_mode="markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


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
    text, keyboard = get_poll_list(session, user)
    update.message.chat.send_message(text, reply_markup=keyboard)


@run_async
@message_wrapper(private=True)
def list_closed_polls(bot, update, session, user):
    """Get a list of all closed polls."""
    text, keyboard = get_poll_list(session, user, closed=True)
    update.message.chat.send_message(text, reply_markup=keyboard)
