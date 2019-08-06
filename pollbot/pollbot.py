"""A bot which checks if there is a new record in the server section of hetzner."""
import logging
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ChosenInlineResultHandler,
    InlineQueryHandler,
    Filters,
    MessageHandler,
    Updater,
)

from pollbot.config import config
from pollbot.i18n import i18n # noqa

from pollbot.telegram.job import (
    message_update_job,
    send_notifications,
    delete_old_updates,
)
from pollbot.telegram.message_handler import handle_private_text
from pollbot.telegram.callback_handler import handle_callback_query
from pollbot.telegram.error_handler import error_callback
from pollbot.telegram.inline_query import search
from pollbot.telegram.inline_result_handler import handle_chosen_inline_result
from pollbot.telegram.commands.poll import (
    create_poll,
    list_polls,
    list_closed_polls,
    delete_all,
    delete_all_closed,
)
from pollbot.telegram.commands.misc import send_help, send_donation_text, change_language
from pollbot.telegram.commands.start import start
from pollbot.telegram.commands.external import notify
from pollbot.telegram.commands.admin import broadcast, test_broadcast, stats

logging.basicConfig(level=config['logging']['log_level'],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize telegram updater and dispatcher
updater = Updater(
    token=config['telegram']['api_key'],
    workers=config['telegram']['worker_count'],
    use_context=True,
    request_kwargs={'read_timeout': 20, 'connect_timeout': 20}
)

dispatcher = updater.dispatcher

# Poll commands
dispatcher.add_handler(CommandHandler('create', create_poll))

# Misc commands
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', send_help))
dispatcher.add_handler(CommandHandler('list', list_polls))
dispatcher.add_handler(CommandHandler('list_closed', list_closed_polls))
dispatcher.add_handler(CommandHandler('delete_all', delete_all))
dispatcher.add_handler(CommandHandler('delete_closed', delete_all_closed))
dispatcher.add_handler(CommandHandler('donations', send_donation_text))
dispatcher.add_handler(CommandHandler('notify', notify))
dispatcher.add_handler(CommandHandler('language', change_language))

# Admin command
dispatcher.add_handler(CommandHandler('broadcast', broadcast))
dispatcher.add_handler(CommandHandler('test_broadcast', test_broadcast))
dispatcher.add_handler(CommandHandler('stats', stats))

# Callback handler
dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))

# InlineQuery handler
dispatcher.add_handler(InlineQueryHandler(search))

# InlineQuery result handler
dispatcher.add_handler(ChosenInlineResultHandler(handle_chosen_inline_result))

minute = 60
hour = 60 * minute
job_queue = updater.job_queue
job_queue.run_repeating(message_update_job, interval=1, first=0, name='Handle poll message update queue')
job_queue.run_repeating(send_notifications, interval=5*minute, first=0, name='Handle notifications and due dates')
job_queue.run_repeating(delete_old_updates, interval=hour, first=0, name='Remove old update entries.')

# Message handler
dispatcher.add_handler(
    MessageHandler(
        Filters.text & Filters.private & (~Filters.update.edited_message) & (~Filters.reply),
        handle_private_text
    ))

# Error handler
dispatcher.add_error_handler(error_callback)
