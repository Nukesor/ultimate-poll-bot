"""Misc commands."""
from telegram.ext import run_async

from pollbot.i18n import i18n
from pollbot.helper.session import session_wrapper
from pollbot.display.misc import get_help_text_and_keyboard
from pollbot.telegram.keyboard import get_donations_keyboard


@run_async
@session_wrapper()
def send_help(bot, update, session, user):
    """Send a help text."""
    text, keyboard = get_help_text_and_keyboard(user, 'intro')

    update.message.chat.send_message(
        text,
        parse_mode='Markdown',
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@run_async
@session_wrapper()
def send_donation_text(bot, update, session, user):
    """Send the donation text."""
    update.message.chat.send_message(
        i18n.t('misc.donation', locale=user.locale),
        parse_mode='Markdown',
        reply_markup=get_donations_keyboard(user)
    )
