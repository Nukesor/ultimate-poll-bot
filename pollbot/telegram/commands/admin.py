"""Admin related stuff."""
import time
from datetime import datetime, timedelta

from sqlalchemy.orm.scoping import scoped_session
from telegram import ReplyKeyboardRemove
from telegram.bot import Bot
from telegram.error import BadRequest, Unauthorized
from telegram.update import Update

from pollbot.decorators import admin_required
from pollbot.models import User
from pollbot.telegram.session import message_wrapper


@message_wrapper()
@admin_required
def reset_broadcast(
    bot: Bot, update: Update, session: scoped_session, user: User
) -> str:
    """Reset the broadcast_sent flag for all users."""
    session.query(User).update({"broadcast_sent": False})
    session.commit()

    return "All broadcast flags resetted"


def remaining_time(total, current, start):
    """Small helper to calculate remaining runtime of a command."""
    elapsed = (datetime.now() - start).seconds
    remaining_factor = total / current
    total_time = elapsed * remaining_factor
    remaining_time = ((total - current) / total) * total_time
    return timedelta(seconds=int(remaining_time))


@message_wrapper()
@admin_required
def broadcast(bot: Bot, update: Update, session: scoped_session, user: User) -> None:

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
    batch_size = 1000
    # Send the broadcast to 1000 users at a time (minimize ram usage)
    while sent_count <= user_count:
        users = (
            session.query(User)
            .filter(User.notifications_enabled.is_(True))
            .filter(User.started.is_(True))
            .filter(User.banned.is_(False))
            .filter(User.broadcast_sent.is_(False))
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

            # We are not allowed to contact this user.
            except Unauthorized:
                user.started = False

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
                chat.send_message(
                    f"Sent to {sent_count} users. Remaining time: {remaining}"
                )

    update.message.chat.send_message("All messages sent")


@message_wrapper()
@admin_required
def test_broadcast(
    bot: Bot, update: Update, session: scoped_session, user: User
) -> None:

    """Send the broadcast message to the admin for test purposes."""
    message = update.message.text.split(" ", 1)[1].strip()

    bot.send_message(
        user.id,
        message,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
