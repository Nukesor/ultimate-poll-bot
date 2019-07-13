"""Admin related stuff."""
import time
from telegram.ext import run_async
from telegram.error import BadRequest, Unauthorized

from pollbot.helper.session import session_wrapper
from pollbot.models import User
from pollbot.config import config


@run_async
@session_wrapper()
def broadcast(bot, update, session, user):
    """Broadcast a message to all users."""
    if user.username.lower() != config['telegram']['admin'].lower():
        return 'You are not allowed to do this'
    message = update.message.text.split(' ', 1)[1].strip()

    users = session.query(User).all()

    update.message.chat.send_message(f'Sending broadcast to {len(users)} chats.')
    for user in users:
        print('sending')
        print(user.id)
        try:
            bot.send_message(user.id, message, parse_mode='Markdown')

        # The chat doesn't exist any longer, delete it
        except BadRequest as e:
            if e.message == 'Chat not found': # noqa
                pass

        # We are not allowed to contact this user.
        except Unauthorized:
            pass

        # Sleep one second to not trigger flood prevention
        time.sleep(1)

    update.message.chat.send_message('All messages sent')


@run_async
@session_wrapper()
def test_broadcast(bot, update, session, user):
    """Send the broadcast message to the admin for test purposes."""
    if user.username.lower() != config['telegram']['admin'].lower():
        return 'You are not allowed to do this'
    message = update.message.text.split(' ', 1)[1].strip()

    bot.send_message(user.id, message, parse_mode='Markdown')
