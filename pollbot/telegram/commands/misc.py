"""Misc commands."""
from telegram.ext import run_async
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.i18n import i18n
from pollbot.helper.session import session_wrapper
from pollbot.telegram.keyboard import get_user_language_keyboard
from pollbot.display.misc import get_help_text_and_keyboard


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
    patreon_url = f'https://patreon.com/nukesor'
    paypal_url = f'https://paypal.me/arnebeer/1'
    buttons = [
        [InlineKeyboardButton(text='Patreon', url=patreon_url)],
        [InlineKeyboardButton(text='Paypal', url=paypal_url)],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    update.message.chat.send_message(
        i18n.t('misc.donation', locale=user.locale),
        parse_mode='Markdown',
        reply_markup=keyboard
    )


@run_async
@session_wrapper()
def change_language(bot, update, session, user):
    """Open the language picker."""
    keyboard = get_user_language_keyboard(user)
    update.message.chat.send_message(
        i18n.t('settings.change_language', locale=user.locale),
        parse_mode='markdown',
        reply_markup=keyboard,
    )
