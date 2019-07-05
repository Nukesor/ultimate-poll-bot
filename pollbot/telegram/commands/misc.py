"""Misc commands."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.session import session_wrapper
from pollbot.telegram.keyboard import get_main_keyboard
from pollbot.helper import (
    help_text,
    donations_text,
)


@session_wrapper()
def send_help(bot, update, session, user):
    """Send a start text."""
    keyboard = get_main_keyboard()
    update.message.chat.send_message(
        help_text,
        parse_mode='Markdown',
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


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

    update.message.chat.send_message(donations_text, parse_mode='Markdown', reply_markup=keyboard)
