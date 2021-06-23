"""Misc commands."""
from sqlalchemy.orm.scoping import scoped_session
from telegram.bot import Bot
from telegram.ext import run_async
from telegram.update import Update

from pollbot.display.misc import get_help_text_and_keyboard
from pollbot.i18n import i18n
from pollbot.models.user import User
from pollbot.telegram.keyboard.misc import get_donations_keyboard
from pollbot.telegram.session import message_wrapper


@run_async
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


@run_async
@message_wrapper()
def send_donation_text(
    bot: Bot, update: Update, session: scoped_session, user: User
) -> None:
    """Send the donation text."""
    update.message.chat.send_message(
        i18n.t("misc.donation", locale=user.locale),
        parse_mode="Markdown",
        reply_markup=get_donations_keyboard(user),
    )
