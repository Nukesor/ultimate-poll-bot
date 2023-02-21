"""Session helper functions."""
import traceback
from datetime import date, datetime, timedelta
from functools import wraps
from typing import Any, Callable, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.orm.scoping import scoped_session
from telegram import Bot, Update
from telegram.error import BadRequest, NetworkError, RetryAfter, TimedOut, Unauthorized
from telegram.ext import CallbackContext

from pollbot.config import config
from pollbot.db import get_session
from pollbot.exceptions import RollbackException
from pollbot.helper import remove_markdown_characters
from pollbot.helper.stats import increase_stat
from pollbot.i18n import i18n
from pollbot.models import User, UserStatistic
from pollbot.sentry import ignore_job_exception, sentry


def job_wrapper(func: Callable[[CallbackContext, Session], Any]):
    """Create a session, handle permissions and exceptions for jobs."""

    def wrapper(context: CallbackContext):
        session = get_session()
        try:
            func(context, session)

            session.commit()
        except Exception as e:
            # Capture all exceptions from jobs.
            # We need to handle those inside the jobs
            if not ignore_job_exception(e):
                if config["logging"]["debug"]:
                    traceback.print_exc()

                if should_report_exception(context, e):
                    sentry.capture_exception(tags={"handler": "job"})

        finally:
            session.close()

    return wrapper


def inline_query_wrapper(func: Callable[[Bot, Update, Session, User], Any]):
    """Create a session, handle permissions and exceptions for inline queries."""

    def wrapper(update: Update, context: CallbackContext):
        session = get_session()
        try:
            user = get_user(session, update.inline_query.from_user)
            if user.banned:
                return

            func(context.bot, update, session, user)

            session.commit()
        except Exception as e:
            if not ignore_exception(e):
                if config["logging"]["debug"]:
                    traceback.print_exc()

                if should_report_exception(context, e):
                    sentry.capture_exception(tags={"handler": "inline_query"})

        finally:
            session.close()

    return wrapper


def inline_result_wrapper(func: Callable[[Bot, Update, Session, User], Any]):
    """Create a session, handle permissions and exceptions for inline results."""

    def wrapper(update: Update, context: CallbackContext):
        session = get_session()
        try:
            user = get_user(session, update.chosen_inline_result.from_user)
            if user.banned:
                return

            func(context.bot, update, session, user)

            session.commit()
        except Exception as e:
            if not ignore_exception(e):
                if config["logging"]["debug"]:
                    traceback.print_exc()

            if should_report_exception(context, e):
                sentry.capture_exception(tags={"handler": "inline_query_result"})

        finally:
            session.close()

    return wrapper


def callback_query_wrapper(func: Callable[[Bot, Update, Session, User], Any]):
    """Create a session, handle permissions and exceptions for callback queries."""

    def wrapper(update: Update, context: CallbackContext):
        user = None
        if context.user_data.get("ban"):
            return

        # Check if the user is temporarily banned and send a message.
        # The check is done via the local telegram cache. This way we can prevent
        # opening a new DB connection for each spam request. (lots of performance)
        temp_ban_time = context.user_data.get("temporary-ban-time")
        if temp_ban_time is not None and temp_ban_time == date.today():
            try:
                update.callback_query.answer(i18n.t("callback.spam"))
            except:  # noqa E722
                pass
            return

        session = get_session()
        try:

            user = get_user(session, update.callback_query.from_user)
            # Cache ban value, so we don't have to lookup the value in our database on each request
            if user.banned:
                context.user_data["ban"] = True
                return

            statistic = get_user_statistics(session, user)

            # Cache temporary-ban time, so we don't have to create a connection to our database
            if statistic.votes > config["telegram"]["max_user_votes_per_day"]:
                update.callback_query.answer(
                    i18n.t("callback.spam", locale=user.locale)
                )
                context.user_data["temporary-ban-time"] = date.today()
                return

            func(context.bot, update, session, user)

            session.commit()

        except RollbackException as e:
            session.rollback()

            update.callback_query.answer(e.message)

        except Exception as e:
            if not ignore_exception(e):
                if config["logging"]["debug"]:
                    traceback.print_exc()

                if should_report_exception(context, e):
                    sentry.capture_exception(
                        tags={
                            "handler": "callback_query",
                        },
                        extra={
                            "query_data": update.callback_query.data,
                        },
                    )

                locale = "English"
                if user is not None:
                    locale = user.locale
                try:
                    update.callback_query.answer(
                        i18n.t("callback.error", locale=locale)
                    )
                except BadRequest as e:
                    # Check if this is a simple query timeout exception
                    if not ignore_exception(e):
                        raise e

        finally:
            session.close()

    return wrapper


def message_wrapper(private=False):
    """Create a session, handle permissions, handle exceptions and prepare some entities."""

    def real_decorator(func: Callable[[Bot, Update, Session, User], Any]):
        """Parametrized decorator closure."""

        @wraps(func)
        def wrapper(update: Update, context: CallbackContext):
            # The user has been banned and already got a message regarding this issue
            if context.user_data.get("banned-message-sent"):
                return

            user = None
            message = None
            session = get_session()
            try:
                if hasattr(update, "message") and update.message:
                    message = update.message
                elif hasattr(update, "edited_message") and update.edited_message:
                    message = update.edited_message
                else:
                    raise Exception(f"Couldn't determine message from update: {update}")

                user = get_user(session, message.from_user)

                # Send a message explaining the user, why they cannot use the bot.
                # Also set a flag, which prevents sending this messages multiple times and thereby prevents DOS attacks.
                if user.banned:
                    if not context.user_data.get("banned-message-sent"):
                        context.user_data["banned-message-sent"] = True

                    message.chat.send_message(
                        "You have been permanently banned from using this bot, either due to spamming or inappropriate behavior."
                        "Please refrain from asking questions in the support group or on Github. There's nothing we can do about this."
                    )
                    return

                # Show an error message, if the users uses the bot in a public chat,
                # when he shouldn't. Also check if we're even allowed to send a message.
                if private and message.chat.type != "private":
                    chat = context.bot.getChat(message.chat.id)
                    if chat.permissions.can_send_messages:
                        message.chat.send_message(
                            "Please do this in a direct conversation with me."
                        )
                    return

                response = func(context.bot, update, session, user)

                session.commit()

                # Respond to user
                if response is not None:
                    message.chat.send_message(response)

            except RollbackException as e:
                session.rollback()

                if message is None:
                    return

                message.chat.send_message(
                    e.message,
                    parse_mode="markdown",
                    disable_web_page_preview=True,
                )

            except Exception as e:
                if not ignore_exception(e):
                    if config["logging"]["debug"]:
                        traceback.print_exc()

                    if should_report_exception(context, e):
                        sentry.capture_exception(
                            tags={
                                "handler": "message",
                            },
                            extra={
                                "update": update.to_dict(),
                                "function": func.__name__,
                            },
                        )

                    locale = "English"
                    if user is not None:
                        locale = user.locale

                    if message is None:
                        return
                    try:
                        message.chat.send_message(
                            i18n.t("misc.error", locale=locale),
                            parse_mode="markdown",
                            disable_web_page_preview=True,
                        )
                    except Exception as e:
                        # It sometimes happens, that an error occurs during sending the
                        # error message. Only capture important exceptions
                        if not ignore_exception(e) and should_report_exception(
                            context, e
                        ):
                            sentry.capture_exception(
                                tags={
                                    "handler": "message",
                                },
                                extra={
                                    "update": update.to_dict(),
                                    "function": func.__name__,
                                },
                            )
                            raise e

            finally:
                # The session might not be there yet
                # We're checking for bans inside this try/catch, which has to
                # happen before session initialization due to performance reasons
                if "session" in locals():
                    session.close()

        return wrapper

    return real_decorator


def get_user(session: scoped_session, tg_user: User) -> User:
    """Get the user from the event."""
    user = session.query(User).get(tg_user.id)
    if user is not None and user.banned:
        return user

    if user is None:
        user = User(tg_user.id, tg_user.username)
        session.add(user)
        try:
            session.commit()
            increase_stat(session, "new_users")
        # Handle race condition for parallel user addition
        # Return the user that has already been created
        # in another session
        except IntegrityError as e:
            session.rollback()
            user = session.query(User).get(tg_user.id)
            if user is None:
                raise e

    if tg_user.username is not None:
        user.username = tg_user.username.lower()

    name = get_name_from_tg_user(tg_user)
    user.name = name

    return user


def get_user_statistics(session: scoped_session, user: User) -> UserStatistic:
    """Ensure user statistics exist for this user.
    We need to track at least some user activity, since there seem to be some users which
    abuse the bot by creating polls and spamming up to 1 million votes per day.

    I really hate doing this, but I don't see another way to prevent DOS attacks
    without tracking at least some numbers.
    """
    user_statistic = session.query(UserStatistic).get((date.today(), user.id))

    if user_statistic is None:
        user_statistic = UserStatistic(user)
        session.add(user_statistic)
        try:
            session.commit()
        # Handle race condition for parallel user statistic creation
        # Return the statistic that has already been created in another session
        except IntegrityError as e:
            session.rollback()
            user_statistic = session.query(UserStatistic).get((date.today(), user.id))
            if user_statistic is None:
                raise e

    return user_statistic


def get_name_from_tg_user(tg_user: User) -> str:
    """Return the best possible name for a User."""
    name = ""
    if tg_user.first_name is not None:
        name = tg_user.first_name
        name += " "
    if tg_user.last_name is not None:
        name += tg_user.last_name

    if tg_user.username is not None and name == "":
        name = tg_user.username

    if name == "":
        name = str(tg_user.id)

    name = remove_markdown_characters(name)

    return name.strip()


def should_report_exception(context: CallbackContext, exception: Exception) -> bool:
    """This function is responsible for client-side exception flood-protection.

    Sentry only allows about 5000 events each month.
    Since there's a lot of traffic on this bot, a single catastrophic event is often
    enough to disable all error reporting for the rest of the month.
    """
    # Initialize on first exception
    if context.bot_data.get("exceptions") is None:
        context.bot_data["exceptions"] = {}

    exceptions = context.bot_data.get("exceptions")

    classname = exception.__class__.__name__
    last_seen = exceptions.get(classname)
    # Allow exceptions seen for the first time
    if last_seen is None:
        exceptions[classname] = datetime.now()
        return True

    # Allow retransmission of exceptions after 5 minutes
    if last_seen < (datetime.now() - timedelta(minutes=5)):
        exceptions[classname] = datetime.now()
        return True

    return False


def ignore_exception(exception: Union[BadRequest, Unauthorized]) -> bool:
    """Check whether we can safely ignore this exception."""
    if type(exception) is BadRequest:
        if (
            exception.message.startswith("Query is too old")
            or exception.message.startswith(
                "Query is too old and response timeout expired or query id is invalid"
            )
            or exception.message.startswith("Schedule_date_invalid")
            or exception.message.startswith("Have no rights to send a message")
            or exception.message.startswith("Not enough rights")
            or exception.message.startswith("Chat_write_forbidden")
            or exception.message.startswith(
                "Not enough rights to send text messages to the chat"
            )
            or exception.message.startswith("Message_id_invalid")
            or exception.message.startswith("Message identifier not specified")
            or exception.message.startswith("Message to edit not found")
            or exception.message.startswith("Chat not found")
            or exception.message.startswith("Not found")
            or exception.message.startswith(
                "Message is not modified: specified new message content"
            )
        ):
            return True

    if type(exception) is Unauthorized:
        if exception.message.lower() == "forbidden: bot was blocked by the user":
            return True
        if exception.message.lower() == "forbidden: message_author_required":
            return True
        if (
            exception.message.lower()
            == "forbidden: bot is not a member of the supergroup chat"
        ):
            return True
        if exception.message.lower() == "forbidden: user is deactivated":
            return True
        if exception.message.lower() == "forbidden: bot was kicked from the group chat":
            return True
        if (
            exception.message.lower()
            == "forbidden: bot was kicked from the supergroup chat"
        ):
            return True
        if exception.message.lower() == "forbidden: chat_write_forbidden":
            return True

    # Poll deletion is asynchronous.
    # As a result, there are a lot of race conditions which can occur.
    #
    # For this reason, I decided to simply ignore all errors that occur if a user
    # tries to interact with a poll that has just been deleted.
    # example exception message:
    # Instance '<Poll at 0x7fb2065a2f98>' has been deleted, or its row is otherwise not present.
    if type(exception) is ObjectDeletedError:
        if "<Poll" in exception.__str__():
            return True

    if type(exception) is TimedOut:
        return True

    if type(exception) is RetryAfter:
        return True

    # Super low level http error
    if type(exception) is NetworkError:
        return True

    return False
