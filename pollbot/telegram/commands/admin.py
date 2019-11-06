"""Admin related stuff."""
import time
from telegram.ext import run_async
from telegram.error import BadRequest, Unauthorized

from pollbot.models import User
from pollbot.config import config
from pollbot.i18n import i18n
from pollbot.helper.session import session_wrapper


def admin_required(function):
    """Return if the poll does not exist in the context object."""
    def wrapper(bot, update, session, user):
        if user.username.lower() != config['telegram']['admin'].lower():
            return(i18n.t('admin.not_allowed', locale=user.locale))

        return function(bot, update, session, user)

    return wrapper


@run_async
@session_wrapper()
@admin_required
def broadcast(bot, update, session, user):
    """Broadcast a message to all users."""
    message = update.message.text.split(' ', 1)[1].strip()
    users = session.query(User).all()

    update.message.chat.send_message(f'Sending broadcast to {len(users)} chats.')
    for user in users:
        try:
            bot.send_message(user.id, message, parse_mode='Markdown')
            user.started = True

        # The chat doesn't exist any longer, delete it
        except BadRequest as e:
            if e.message == 'Chat not found':  # noqa
                pass

        # We are not allowed to contact this user.
        except Unauthorized:
            user.started = False
            pass

        # Sleep one second to not trigger flood prevention
        time.sleep(0.07)

    update.message.chat.send_message('All messages sent')


@run_async
@session_wrapper()
@admin_required
def test_broadcast(bot, update, session, user):
    """Send the broadcast message to the admin for test purposes."""
    message = update.message.text.split(' ', 1)[1].strip()

    bot.send_message(user.id, message, parse_mode='Markdown')
