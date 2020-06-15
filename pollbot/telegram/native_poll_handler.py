"""Handle messages."""

from sqlalchemy.orm import Session
from telegram import Update, Bot, Poll as NativePoll
from telegram.ext import run_async

from pollbot.display import User
from pollbot.display.creation import get_native_poll_merged_text
from pollbot.helper.native_polls import merge_from_native_poll
from pollbot.helper.session import message_wrapper
from pollbot.i18n import i18n
from pollbot.models import Poll
from pollbot.telegram.keyboard import (
    get_replace_current_creation_keyboard,
    get_native_poll_merged_keyboard,
)


@run_async
@message_wrapper(private=True)
def create_from_native_poll(bot: Bot, update: Update, session: Session, user: User):
    native_poll: NativePoll = update.message.poll

    if user.current_poll is not None and not user.current_poll.created:
        update.effective_chat.send_message(
            i18n.t("creation.already_creating_ask_replace", locale=user.locale),
            reply_markup=get_replace_current_creation_keyboard(user.current_poll),
        )
        return

    poll = Poll.create(user, session)
    merge_from_native_poll(poll, native_poll, session)

    text = get_native_poll_merged_text(poll)
    keyboard = get_native_poll_merged_keyboard(poll)

    update.effective_chat.send_message(
        text,
        parse_mode="markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@run_async
def send_error_quiz_unsupported(update: Update, _context):
    update.effective_chat.send_message(i18n.t("creation.native_poll.quiz_unsupported"))
