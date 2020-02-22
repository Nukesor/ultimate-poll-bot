"""A bot which checks if there is a new record in the server section of hetzner."""
import logging

# Initialize config, client and the asyncio loop
from pollbot.client import config, client, loop
# Early import to initialize i18n
from pollbot.i18n import i18n

from pollbot.telegram.job import (
    message_update_job,
    send_notifications,
    create_daily_stats,
)
#from pollbot.telegram.message_handler import handle_private_text
#from pollbot.telegram.callback_handler import handle_callback_query
#from pollbot.telegram.inline_query import search
#from pollbot.telegram.inline_result_handler import handle_chosen_inline_result
from pollbot.telegram.commands.poll import (
    create_poll,
    list_polls,
    list_closed_polls,
)
from pollbot.telegram.commands.misc import send_help, send_donation_text
from pollbot.telegram.commands.start import start
from pollbot.telegram.commands.external import notify
from pollbot.telegram.commands.admin import (
    broadcast,
    reset_broadcast,
    test_broadcast,
)
from pollbot.telegram.commands.user import open_user_settings_command

logging.basicConfig(level=config['logging']['log_level'],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Schedule jobs
loop.create_task(message_update_job())
loop.create_task(send_notifications())
loop.create_task(create_daily_stats())


# Message handler
#dispatcher.add_handler(
#    MessageHandler(
#        Filters.text & Filters.private & (~Filters.update.edited_message) & (~Filters.reply),
#        handle_private_text
#    ))
