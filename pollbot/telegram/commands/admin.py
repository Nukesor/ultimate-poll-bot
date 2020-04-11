"""Admin related stuff."""
import time
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
        if user.username.lower() != config['telegram']['admin'].lower():
            return(i18n.t('admin.not_allowed', locale=user.locale))

        return function(bot, update, session, user)

    return wrapper


@run_async
@message_wrapper()
@admin_required
def reset_broadcast(bot, update, session, user):
    """Reset the broadcast_sent flag for all users."""
    session.query(User).update({'broadcast_sent': False})
    session.commit()

    return "All broadcast flags resetted"


@run_async
@message_wrapper()
@admin_required
def broadcast(bot, update, session, user):
    """Broadcast a message to all users."""
    chat = update.message.chat
    message = update.message.text.split(' ', 1)[1].strip()
    users = session.query(User) \
        .filter(User.notifications_enabled.is_(True)) \
        .filter(User.started.is_(True)) \
        .filter(User.broadcast_sent.is_(False)) \
        .all()

    chat.send_message(f'Sending broadcast to {len(users)} chats.')
    count = 0
    for user in users:
        try:
            bot.send_message(
                user.id,
                message,
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardRemove(),
            )
            user.broadcast_sent = True
            session.commit()

        # The chat doesn't exist any longer, delete it
        except BadRequest as e:
            if e.message == 'Chat not found':  # noqa
                pass

        # We are not allowed to contact this user.
        except Unauthorized:
            user.started = False
            pass

        except TimeoutError:
            pass

        # Sleep one second to not trigger flood prevention
        time.sleep(0.07)

        count += 1
        if count % 500 == 0:
            chat.send_message(f'Sent to {count} users.')

    update.message.chat.send_message('All messages sent')


@run_async
@message_wrapper()
@admin_required
def test_broadcast(bot, update, session, user):
    """Send the broadcast message to the admin for test purposes."""
    message = update.message.text.split(' ', 1)[1].strip()

    bot.send_message(
        user.id,
        message,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove(),
    )
