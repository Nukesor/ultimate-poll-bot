"""Admin related stuff."""
import time
from datetime import datetime, timedelta
from telegram import ReplyKeyboardRemove
from telegram.ext import run_async
from telegram.error import BadRequest, Unauthorized

from pollbot.models import User
from pollbot.config import config
from pollbot.i18n import i18n
from pollbot.helper.session import message_wrapper


def admin_required(function):
    """Return if the poll does not exist in the context object."""

    def wrapper(bot, update, session, user):
        if user.username.lower() != config["telegram"]["admin"].lower():
            return i18n.t("admin.not_allowed", locale=user.locale)

        return function(bot, update, session, user)

    return wrapper


@run_async
@message_wrapper()
@admin_required
def reset_broadcast(bot, update, session, user):
    """Reset the broadcast_sent flag for all users."""
    session.query(User).update({"broadcast_sent": False})
    session.commit()

    return "All broadcast flags resetted"


def remaining_time(total, current, start):
    """Small helper to calculate remaining runtime of a command."""
    diff = datetime.now() - start
    remaining_factor = total/current
    remaining_time = timedelta(seconds=diff.seconds*remaining_factor)
    return remaining_time - timedelta(microseconds=remaining_time.microseconds)


@run_async
@message_wrapper()
@admin_required
def broadcast(bot, update, session, user):
    """Broadcast a message to all users."""
    chat = update.message.chat
    message = update.message.text.split(" ", 1)[1].strip()
    user_count = (
        session.query(User)
        .filter(User.notifications_enabled.is_(True))
        .filter(User.started.is_(True))
        .filter(User.banned.is_(False))
        .filter(User.broadcast_sent.is_(False))
        .count()
    )


    start_time = datetime.now()
    chat.send_message(f"Sending broadcast to {user_count} chats.")

    sent_count = 0
    offset = 0
    batch_size = 1000
    # Send the broadcast to 1000 users at a time (minimize ram usage)
    while offset <= user_count:
        users = (
            session.query(User)
            .filter(User.notifications_enabled.is_(True))
            .filter(User.started.is_(True))
            .filter(User.banned.is_(False))
            .filter(User.broadcast_sent.is_(False))
            .offset(offset)
            .limit(batch_size)
            .all()
        )

        for user in users:
            try:
                bot.send_message(
                    user.id,
                    message,
                    parse_mode="Markdown",
                    reply_markup=ReplyKeyboardRemove(),
                )
                user.broadcast_sent = True

            # The chat does no longer exist, delete it
            except BadRequest as e:
                if e.message == "Chat not found":  # noqa
                    user.started = False
                    pass

            # We are not allowed to contact this user.
            except Unauthorized:
                user.started = False
                pass

            except TimeoutError:
                pass

            session.commit()
            # Sleep a little bit to not trigger flood prevention
            time.sleep(0.07)

            sent_count += 1
            if sent_count == 500:
                remaining = remaining_time(user_count, sent_count, start_time)
                chat.send_message(f"First 500 are done. Remaining time: {remaining}")

            if sent_count % 5000 == 0:
                remaining = remaining_time(user_count, sent_count, start_time)
                chat.send_message(f"Sent to {sent_count} users. Remaining time: {remaining}")

        offset += batch_size

    update.message.chat.send_message("All messages sent")


@run_async
@message_wrapper()
@admin_required
def test_broadcast(bot, update, session, user):
    """Send the broadcast message to the admin for test purposes."""
    message = update.message.text.split(" ", 1)[1].strip()

    bot.send_message(
        user.id, message, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(),
    )
