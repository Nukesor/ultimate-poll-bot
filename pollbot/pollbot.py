"""A bot which checks if there is a new record in the server section of hetzner."""
import logging

from telegram.ext import (
    CallbackQueryHandler,
    ChosenInlineResultHandler,
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

from pollbot.config import config
from pollbot.telegram.callback_handler import (
    handle_async_callback_query,
    handle_callback_query,
)
from pollbot.telegram.callback_handler.mapping import (
    get_async_callback_mapping_regex,
    get_callback_mapping_regex,
)
from pollbot.telegram.commands.admin import broadcast, reset_broadcast, test_broadcast
from pollbot.telegram.commands.external import notify
from pollbot.telegram.commands.misc import send_help
from pollbot.telegram.commands.poll import (
    cancel_poll_creation,
    create_poll,
    list_closed_polls,
    list_polls,
)
from pollbot.telegram.commands.start import start
from pollbot.telegram.commands.user import delete_me, open_user_settings_command, stop
from pollbot.telegram.filters import CustomFilters
from pollbot.telegram.inline_query import search
from pollbot.telegram.inline_result_handler import handle_chosen_inline_result
from pollbot.telegram.job import (
    cleanup,
    create_daily_stats,
    delete_polls,
    message_update_job,
    perma_ban_checker,
    send_notifications,
)
from pollbot.telegram.message_handler import handle_private_text
from pollbot.telegram.native_poll_handler import (
    create_from_native_poll,
    send_error_quiz_unsupported,
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

command_filter = ~Filters.update.edited_message
# Poll commands
dispatcher.add_handler(
    CommandHandler(
        ["create", "new", "add"],
        create_poll,
        filters=command_filter,
        run_async=True,
    )
)
dispatcher.add_handler(
    CommandHandler(
        ["cancel", "abort"],
        cancel_poll_creation,
        filters=command_filter,
        run_async=True,
    )
)

# Misc commands
dispatcher.add_handler(
    CommandHandler(
        "start",
        start,
        filters=command_filter,
        run_async=True,
    )
)
dispatcher.add_handler(
    CommandHandler(
        "stop",
        stop,
        filters=command_filter,
        run_async=True,
    )
)
dispatcher.add_handler(
    CommandHandler(
        "delete_me",
        delete_me,
        filters=command_filter,
        run_async=True,
    )
)
dispatcher.add_handler(
    CommandHandler(
        "settings",
        open_user_settings_command,
        filters=command_filter,
        run_async=True,
    )
)
dispatcher.add_handler(
    CommandHandler(
        "help",
        send_help,
        filters=command_filter,
        run_async=True,
    )
)
dispatcher.add_handler(
    CommandHandler(
        "list",
        list_polls,
        filters=command_filter,
        run_async=True,
    )
)
dispatcher.add_handler(
    CommandHandler(
        "list_closed",
        list_closed_polls,
        filters=command_filter,
        run_async=True,
    )
)

# External commands
dispatcher.add_handler(
    CommandHandler(
        "notify",
        notify,
        filters=command_filter,
        run_async=True,
    )
)

# Admin command
dispatcher.add_handler(
    CommandHandler(
        "broadcast",
        broadcast,
        filters=command_filter,
        run_async=True,
    )
)
dispatcher.add_handler(
    CommandHandler(
        "reset_broadcast",
        reset_broadcast,
        filters=command_filter,
        run_async=True,
    )
)
dispatcher.add_handler(
    CommandHandler(
        "test_broadcast",
        test_broadcast,
        filters=command_filter,
        run_async=True,
    )
)

# Poll handler
dispatcher.add_handler(
    MessageHandler(
        Filters.poll & ~CustomFilters.quiz & Filters.chat_type.private,
        create_from_native_poll,
        run_async=True,
    )
)
dispatcher.add_handler(
    MessageHandler(
        CustomFilters.quiz & Filters.chat_type.private,
        send_error_quiz_unsupported,
        run_async=True,
    )
)

# Callback handler
dispatcher.add_handler(
    CallbackQueryHandler(handle_callback_query, pattern=get_callback_mapping_regex())
)
dispatcher.add_handler(
    CallbackQueryHandler(
        handle_async_callback_query,
        pattern=get_async_callback_mapping_regex(),
        run_async=True,
    )
)

# InlineQuery handler
dispatcher.add_handler(InlineQueryHandler(search, run_async=True))

# InlineQuery result handler
dispatcher.add_handler(
    ChosenInlineResultHandler(handle_chosen_inline_result, run_async=True)
)

minute = 60
hour = 60 * minute
job_queue = updater.job_queue
job_queue.run_repeating(
    delete_polls,
    interval=5,
    first=0,
    name="Delete polls that are scheduled for deletion.",
)
job_queue.run_repeating(
    message_update_job, interval=10, first=0, name="Handle poll message update queue."
)
job_queue.run_repeating(
    send_notifications,
    interval=5 * minute,
    first=0,
    name="Handle notifications and due dates.",
)
job_queue.run_repeating(
    create_daily_stats,
    interval=6 * hour,
    first=0,
    name="Create daily statistic entities.",
)
job_queue.run_repeating(
    perma_ban_checker,
    interval=1 * hour,
    first=0,
    name="Perma-ban users that continuously reach thresholds.",
)
job_queue.run_repeating(
    cleanup,
    interval=15 * minute,
    first=10,
    name="Remove old data",
)

# Message handler
dispatcher.add_handler(
    MessageHandler(
        Filters.text
        & Filters.chat_type.private
        & (~Filters.update.edited_message)
        & (~Filters.reply)
        & (~Filters.update.channel_posts),
        handle_private_text,
    )
)
