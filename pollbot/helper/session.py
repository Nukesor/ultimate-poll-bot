"""Session helper functions."""
import traceback
from functools import wraps
from telethon import types
from telethon.events import StopPropagation
from telethon.errors.rpcbaseerrors import (
    ForbiddenError,
)
from sqlalchemy.exc import IntegrityError

from pollbot.client import client, client_id
from pollbot.config import config
from pollbot.db import get_session
from pollbot.sentry import sentry
from pollbot.models import User
from pollbot.i18n import i18n
from pollbot.helper.stats import increase_stat


def job_session_wrapper():
    """Create a session, handle permissions and exceptions for jobs."""
    def real_decorator(func):
        """Parametrized decorator closure."""
        @wraps(func)
        def wrapper(context):
            session = get_session()
            try:
                func(context, session)

                session.commit()
            except Exception as e:
                # Capture all exceptions from jobs. We need to handle those inside the jobs
                if not ignore_job_exception(e):
                    if config['logging']['debug']:
                        traceback.print_exc()
                    sentry.captureException()
            finally:
                session.close()
        return wrapper

    return real_decorator


def hidden_session_wrapper():
    """Create a session, handle permissions and exceptions."""
    def real_decorator(func):
        """Parametrized decorator closure."""
        @wraps(func)
        def wrapper(update, context):
            session = get_session()
            try:
                user = get_user(session, update)

                func(context.bot, update, session, user)

                session.commit()
            except Exception as e:
                if not ignore_exception(e):
                    if config['logging']['debug']:
                        traceback.print_exc()
                    sentry.captureException()

                if hasattr(update, 'callback_query') and update.callback_query is not None:
                    locale = 'English'
                    if user is not None:
                        locale = user.locale
                    update.callback_query.answer(i18n.t('callback.error', locale=locale))
            finally:
                session.close()
        return wrapper

    return real_decorator


def message_wrapper(respond_on_error=True, private=False):
    """Create a session for functions handling messages.

    Handle permissions, exceptions and prepares some entities we
    almost always need.
    """
    def real_decorator(func):
        """Parametrized decorator closure."""
        @wraps(func)
        async def wrapper(event):
            session = get_session()
            try:
                # We aren't interested in messages from broadcast channels
                if event.post:
                    return

                # Get the current user.
                # User can be None, if the message was sent from a chat
                user = await get_message_user(event, session)
                if user is None:
                    return

                if not await ensure_private(event, user, private=private):
                    return

                try:
                    response = await func(event, session, user)
                except StopPropagation as e:
                    # In case we don't want propagation,
                    # close the session and raise the exception
                    session.commit()
                    raise e
                return response

                session.commit()
                # Respond to user
                if response is not None:
                    await event.respond(response)

            except StopPropagation as e:
                # Continue propagation
                # We do this twice to catch any errors that might occur
                # during session.commit()
                session.close()
                raise e

            except Exception as e:
                if not ignore_exception(e):
                    if config['logging']['debug']:
                        traceback.print_exc()
                    sentry.captureException()

                if respond_on_error:
                    locale = 'English'
                    if user is not None:
                        locale = user.locale
                    session.close()
                    await event.respond(
                        i18n.t('misc.error', locale=locale),
                        link_preview=False,
                    )

            finally:
                session.close()

        return wrapper

    return real_decorator


async def get_message_user(event, session):
    """Get the user from the update.

        Return None, if there is no user.
    """
    user_id = event.from_id
    user = session.query(User).get(user_id)
    if user is not None:
        return user

    tg_user = await client.get_entity(user_id)
    user = User(user_id, tg_user.username)
    session.add(user)

    try:
        session.commit()
        increase_stat(session, 'new_users')
    # Handle race condition for parallel user addition
    # Return the user that has already been created
    # in another session
    except IntegrityError as e:
        session.rollback()
        user = session.query(User).get(user_id)
        if user is None:
            raise e
        return user

    user.username = tg_user.username.lower()
    name = get_name_from_tg_user(tg_user)
    user.name = name

    return user


def get_name_from_tg_user(tg_user):
    """Get a username from a user.

    Try to get any name first, fallback to id.
    """
    if tg_user.username:
        name = tg_user.username
    elif tg_user.first_name:
        name = tg_user.first_name
    elif tg_user.last_name:
        name = tg_user.last_name
    else:
        name = str(tg_user.id)

    for character in ['[', ']', '_', '*', '`']:
        name = name.replace(character, f'\\{character}')

    return name.strip()


async def ensure_private(event, user, private=False):
    """Check whether the user is allowed to access this endpoint."""
    peer_id, peer_type = get_peer_information(event.to_id)
    if private and peer_id != client_id:
        await event.respond('Please do this in a direct conversation with me.')
        return False

    return True


def ignore_exception(exception):
    """Check whether we can safely ignore this exception."""
    if isinstance(exception, ForbiddenError):
        return True

    return False


def ignore_job_exception(exception):
    """Check whether we can safely ignore this exception in jobs."""
    if isinstance(exception, ForbiddenError):
        return True

    return False


def get_peer_information(peer):
    """Get the id depending on the chat type."""
    if isinstance(peer, types.PeerUser):
        return peer.user_id, 'user'
    elif isinstance(peer, types.PeerChat):
        return peer.chat_id, 'peer'
    elif isinstance(peer, types.PeerChannel):
        return peer.channel_id, 'channel'
    else:
        raise Exception("Unknown chat type")
