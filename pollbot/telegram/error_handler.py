"""Telegram bot error handling."""
import traceback
from telegram.error import (
    BadRequest,
    NetworkError,
    TimedOut,
    Unauthorized,
)

from pollbot.i18n import i18n
from pollbot.sentry import sentry


def error_callback(update, context):
    """Handle generic errors from telegram."""
    try:
        raise context.error
    except (TimedOut, NetworkError):
        pass
    except BadRequest as e:
        # It took to long to send the inline query response.
        # Probably due to slow network on client side.
        if str(e) == 'Query_id_invalid': # noqa
            return

        traceback.print_exc()
        sentry.captureException()
    # A user banned the bot Just ignore this.
    # This probably happens due to sending a message during maintenance work
    except Unauthorized:
        pass

    except: # noqa
        if hasattr(update, 'callback_query') and update.callback_query is not None:
            update.callback_query.answer(i18n.t('callback.error'))
        traceback.print_exc()
        sentry.captureException()
