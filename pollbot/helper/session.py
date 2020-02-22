"""Session helper functions."""
import asyncio
from datetime import datetime, timedelta
import traceback
from functools import wraps
from telethon.events import StopPropagation
from telethon.errors.rpcbaseerrors import (
    ForbiddenError,
)
from telethon.errors.rpcerrorlist import (
    MessageNotModifiedError,
)
from sqlalchemy.exc import IntegrityError

from pollbot.client import client, client_id
from pollbot.config import config
from pollbot.db import get_session
from pollbot.sentry import sentry
from pollbot.models import User
from pollbot.i18n import i18n
from pollbot.helper.stats import increase_stat
from pollbot.helper import get_peer_information


def job_wrapper(wait=1):
    """Create a session and handle exceptions for jobs."""
    def real_decorator(func):
        """Parametrized decorator closure."""
        @wraps(func)
        async def wrapper():
            session = get_session()
            # Run the job in an endless loop
            # Catch exceptions and report them to sentry.
            # Also wait for a specified amount of time between every loop
            while True:
                try:
                    await func(session)

                    session.commit()
                except Exception as e:
                    # Capture all exceptions from jobs. We need to handle those inside the jobs
                    if not ignore_job_exception(e):
                        if config['logging']['debug']:
                            traceback.print_exc()
                        sentry.captureException()
                    session.rollback()
                finally:
                    session.close()

                await asyncio.sleep(wait)

        return wrapper

    return real_decorator


def callback_wrapper():
    """Create a session, handle permissions and exceptions."""
    def real_decorator(func):
        """Parametrized decorator closure."""
        @wraps(func)
        async def wrapper(event):
            session = get_session()
            try:
                user = None
                user = await get_user(session, event.query.user_id)

                await func(session, event, user)

                session.commit()
            except Exception as e:
                if not ignore_exception(e):
                    if config['logging']['debug']:
                        traceback.print_exc()
                    sentry.captureException()

                locale = 'English'
                if user is not None:
                    locale = user.locale
                await event.answer(i18n.t('callback.error', locale=locale))
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
                user = await get_user(session, event.from_id)

                if not await ensure_private(event, user, private=private):
                    return

                try:
                    response = await func(event, session, user)
                except StopPropagation as e:
                    # In case we don't want propagation,
                    # close the session and raise the exception
                    session.commit()
                    raise e

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
                    await event.respond(
                        i18n.t('misc.error', locale=locale),
                        link_preview=False,
                    )

            finally:
                session.close()

        return wrapper

    return real_decorator


async def get_user(session, user_id):
    """Get the user from the event."""
    user = session.query(User).get(user_id)
    tg_user = None
    if user is None:
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

    # Update user info (username etc.) if the user hasn't been updated
    # in the last three days
    three_days_ago = datetime.now() - timedelta(days=3)
    if user.last_update is not None and user.last_update >= three_days_ago:
        return user

    if tg_user is None:
        tg_user = await client.get_entity(user_id)

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
    if isinstance(exception, MessageNotModifiedError):
        return True

    return False


def ignore_job_exception(exception):
    """Check whether we can safely ignore this exception in jobs."""
    if isinstance(exception, ForbiddenError):
        return True

    return False
