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
from pollbot.i18n import i18n

from pollbot.telegram.job import (
    message_update_job,
    send_notifications,
    create_daily_stats,
    perma_ban_checker,
    cleanup,
)
from pollbot.telegram.message_handler import handle_private_text
from pollbot.telegram.callback_handler import (
    handle_async_callback_query,
    handle_callback_query,
)
from pollbot.telegram.callback_handler.mapping import (
    get_callback_mapping_regex,
    get_async_callback_mapping_regex,
)
from pollbot.telegram.inline_query import search
from pollbot.telegram.inline_result_handler import handle_chosen_inline_result
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
from pollbot.telegram.commands.user import (
    open_user_settings_command,
    stop,
)

logging.basicConfig(
    level=config["logging"]["log_level"],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize telegram updater and dispatcher
updater = Updater(
    token=config["telegram"]["api_key"],
    workers=config["telegram"]["worker_count"],
    use_context=True,
    request_kwargs={"read_timeout": 20, "connect_timeout": 20},
)

dispatcher = updater.dispatcher

# Poll commands
dispatcher.add_handler(CommandHandler("create", create_poll))

# Misc commands
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("stop", stop))
dispatcher.add_handler(CommandHandler("settings", open_user_settings_command))
dispatcher.add_handler(CommandHandler("help", send_help))
dispatcher.add_handler(CommandHandler("list", list_polls))
dispatcher.add_handler(CommandHandler("list_closed", list_closed_polls))
dispatcher.add_handler(CommandHandler("donations", send_donation_text))

# External commands
dispatcher.add_handler(CommandHandler("notify", notify))

# Admin command
dispatcher.add_handler(CommandHandler("broadcast", broadcast))
dispatcher.add_handler(CommandHandler("reset_broadcast", reset_broadcast))
dispatcher.add_handler(CommandHandler("test_broadcast", test_broadcast))

# Callback handler
dispatcher.add_handler(CallbackQueryHandler(handle_callback_query, pattern=get_callback_mapping_regex()))
dispatcher.add_handler(CallbackQueryHandler(handle_async_callback_query, pattern=get_async_callback_mapping_regex()))

# InlineQuery handler
dispatcher.add_handler(InlineQueryHandler(search))

# InlineQuery result handler
dispatcher.add_handler(ChosenInlineResultHandler(handle_chosen_inline_result))

minute = 60
hour = 60 * minute
job_queue = updater.job_queue
job_queue.run_repeating(
    message_update_job, interval=10, first=0, name="Handle poll message update queue"
)
job_queue.run_repeating(
    send_notifications,
    interval=5 * minute,
    first=0,
    name="Handle notifications and due dates",
)
job_queue.run_repeating(
    create_daily_stats,
    interval=6 * hour,
    first=0,
    name="Create daily statistic entities",
)
job_queue.run_repeating(
    perma_ban_checker,
    interval=1 * hour,
    first=0,
    name="Perma-ban users that continuously reach thresholds.",
)
job_queue.run_repeating(
    cleanup, interval=6 * hour, first=0, name="Remove old data",
)

# Message handler
dispatcher.add_handler(
    MessageHandler(
        Filters.text
        & Filters.private
        & (~Filters.update.edited_message)
        & (~Filters.reply),
        handle_private_text,
    )
)
