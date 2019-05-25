"""A bot which checks if there is a new record in the server section of hetzner."""
import logging
from telegram.ext import (
    CommandHandler,
    Updater,
)

from pollbot.config import config
from pollbot.helper.session import session_wrapper
from pollbot.helper.telegram import call_tg_func
from pollbot.telegram.error_handler import error_callback

from pollbot.helper import (
    start_text,
    help_text,
    donations_text,
)


@session_wrapper()
def start(bot, update, session, chat, user):
    """Send a help text."""
    if chat.is_maintenance or chat.is_newsfeed:
        call_tg_func(update.message.chat, 'send_message', ['Hello there'],
                     {'reply_markup': get_main_keyboard()})
    else:
        call_tg_func(update.message.chat, 'send_message', [start_text],
                     {'parse_mode': 'Markdown'})


@session_wrapper()
def send_help_text(bot, update, session, chat, user):
    """Send a help text."""
    if user.admin:
        call_tg_func(update.message.chat, 'send_message', [help_text],
                     {'parse_mode': 'Markdown'})
    elif not user.admin:
        call_tg_func(update.message.chat, 'send_message', [help_text],
                     {'parse_mode': 'Markdown'})


@session_wrapper()
def send_donation_text(bot, update, session, chat, user):
    """Send the donation text."""
    call_tg_func(update.message.chat, 'send_message', [donations_text],
                 {'parse_mode': 'Markdown'})


logging.basicConfig(level=config.LOG_LEVEL,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize telegram updater and dispatcher
updater = Updater(token=config.TELEGRAM_API_KEY, workers=config.WORKER_COUNT, use_context=True,
                  request_kwargs={'read_timeout': 20, 'connect_timeout': 20})


dispatcher = updater.dispatcher
# Create group message handler

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_error_handler(error_callback)
