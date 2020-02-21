"""Admin related stuff."""
import re
import time
from telethon import events
from telethon.errors.rpcbaseerrors import (
    ForbiddenError,
)

from pollbot.client import client
from pollbot.models import User
from pollbot.config import config
from pollbot.i18n import i18n
from pollbot.helper.session import message_wrapper


def admin_required(function):
    """Return if the poll does not exist in the context object."""
    async def wrapper(event, session, user):
        if user.username.lower() != config['telegram']['admin'].lower():
            await event.respond(i18n.t('admin.not_allowed', locale=user.locale))
            return

        return await function(event, session, user)

    return wrapper


@client.on(events.NewMessage(incoming=True, pattern='/reset_broadcast'))
@message_wrapper(private=True)
@admin_required
async def reset_broadcast(event, session, user):
    """Reset the broadcast_sent flag for all users."""
    session.query(User).update({'broadcast_sent': False})
    session.commit()

    await event.respond("All broadcast flags resetted")
    raise events.StopPropagation


@client.on(
    events.NewMessage(
        incoming=True,
        pattern=re.compile('/broadcast.*', re.DOTALL)
    ))
@message_wrapper(private=True)
@admin_required
async def broadcast(event, session, user):
    """Broadcast a message to all users."""
    message = event.text.split(' ', 1)[1].strip()
    users = session.query(User) \
        .filter(User.notifications_enabled.is_(True)) \
        .filter(User.started.is_(True)) \
        .filter(User.broadcast_sent.is_(False)) \
        .all()

    await event.respond(f'Sending broadcast to {len(users)} chats.')
    count = 0
    for user in users:
        try:
            await client.send_message(user.id, message, link_preview=False)
            user.broadcast_sent = True
            session.commit()

#        # The chat doesn't exist any longer, delete it
#        except BadRequest as e:
#            if e.message == 'Chat not found':  # noqa
#                pass

        # We are not allowed to contact this user.
        except ForbiddenError:
            user.started = False
            pass

        # Sleep one second to not trigger flood prevention
        time.sleep(0.07)

        count += 1
        if count % 500 == 0:
            await event.respond(f'Sent to {count} users.')

    await event.respond('All messages sent')
    raise events.StopPropagation


@client.on(
    events.NewMessage(
        incoming=True,
        pattern=re.compile('/test_broadcast.*', re.DOTALL)
    ))
@message_wrapper(private=True)
@admin_required
async def test_broadcast(event, session, user):
    """Send the broadcast message to the admin for test purposes."""
    message = event.text.split(' ', 1)[1].strip()

    await event.respond(message)
    raise events.StopPropagation
