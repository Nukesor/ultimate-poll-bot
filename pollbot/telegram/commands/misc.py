"""Misc commands."""
from sqlalchemy.orm.scoping import scoped_session
from telegram.bot import Bot
from telegram.update import Update

from pollbot.display.misc import get_help_text_and_keyboard
from pollbot.models.user import User
from pollbot.telegram.session import message_wrapper


@message_wrapper()
def send_help(bot: Bot, update: Update, session: scoped_session, user: User) -> None:
    """Send a help text."""
    text, keyboard = get_help_text_and_keyboard(user, "intro")

    update.message.chat.send_message(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
