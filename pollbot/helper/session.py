"""Session helper functions."""
import traceback
from functools import wraps
from telegram.error import (
    BadRequest,
    Unauthorized,
    TimedOut,
)

from pollbot.db import get_session
from pollbot.sentry import sentry
from pollbot.models import User
from pollbot.i18n import i18n


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
            except: # noqa
                # Capture all exceptions from jobs. We need to handle those inside the jobs
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
                if not is_allowed(user, update):
                    return

                func(context.bot, update, session, user)

                session.commit()
            # Handle all not telegram relatated exceptions
            except Exception as e:
                if not ignore_exception(e):
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


def session_wrapper(send_message=True, private=False):
    """Create a session, handle permissions, handle exceptions and prepare some entities."""
    def real_decorator(func):
        """Parametrized decorator closure."""
        @wraps(func)
        def wrapper(update, context):
            session = get_session()
            try:
                user = get_user(session, update)
                if not is_allowed(user, update, private=private):
                    return

                if hasattr(update, 'message') and update.message:
                    message = update.message
                elif hasattr(update, 'edited_message') and update.edited_message:
                    message = update.edited_message

                if not is_allowed(user, update, private=private):
                    return

                response = func(context.bot, update, session, user)

                session.commit()
                # Respond to user
                if hasattr(update, 'message') and response is not None:
                    message.chat.send_message(response)

            # Handle all not telegram relatated exceptions
            except Exception as e:
                if ignore_exception(e):
                    pass

                traceback.print_exc()
                sentry.captureException()
                if send_message:
                    locale = 'English'
                    if user is not None:
                        locale = user.locale
                    session.close()
                    message.chat.send_message(
                        i18n.t('misc.error', locale=locale),
                        parse_mode='markdown',
                        disable_web_page_preview=True,
                    )

            finally:
                session.close()

        return wrapper

    return real_decorator


def get_user(session, update):
    """Get the user from the update."""
    user = None
    # Check user permissions
    if hasattr(update, 'message') and update.message:
        user = User.get_or_create(session, update.message.from_user)
    if hasattr(update, 'edited_message') and update.edited_message:
        user = User.get_or_create(session, update.edited_message.from_user)
    elif hasattr(update, 'inline_query') and update.inline_query:
        user = User.get_or_create(session, update.inline_query.from_user)
    elif hasattr(update, 'callback_query') and update.callback_query:
        user = User.get_or_create(session, update.callback_query.from_user)

    return user


def is_allowed(user, update, private=False):
    """Check whether the user is allowed to access this endpoint."""
    if private and update.message.chat.type != 'private':
        update.message.chat.send_message('Please do this in a direct conversation with me.')
        return False

    return True


def ignore_exception(exception):
    """Check whether we can safely ignore this exception."""
    if isinstance(exception, BadRequest):
        if exception.message.startswith('Query is too old') or \
           exception.message.startswith('Have no rights to send a message') or \
           exception.message.startswith('Message is not modified: specified new message content'):
            return True

    if isinstance(exception, Unauthorized):
        if exception.message == 'Forbidden: bot was blocked by the user':
            return True
        if exception.message == 'Forbidden: MESSAGE_AUTHOR_REQUIRED':
            return True
        if exception.message == 'Forbidden: bot is not a member of the supergroup chat':
            return True
        if exception.message == 'Forbidden: user is deactivated':
            return True

    if isinstance(exception, TimedOut):
        return True

    return False
