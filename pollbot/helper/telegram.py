"""All helper for interaction with telegram."""
import time
import logging
from datetime import datetime
from telegram.error import TimedOut, NetworkError
from raven import breadcrumbs

from pollbot.sentry import sentry
from pollbot.config import config


def call_tg_func(tg_object: object, function_name: str,
                 args: list = None, kwargs: dict = None):
    """Call a tg object member function.

    We need to handle those calls in case we get rate limited.
    """
    _try = 0
    tries = 2
    exception = None

    while _try < tries:
        try:
            args = args if args else []
            kwargs = kwargs if kwargs else {}
            breadcrumbs.record(data={'action': f'Starting: {datetime.now()}'}, category='info')
            retrieved_object = getattr(tg_object, function_name)(*args, **kwargs)
            return retrieved_object

        except (TimedOut, NetworkError) as e:
            # Can't update message. just ignore it
            if 'Message to edit not found' in str(e) or \
                    'Message is not modified' in str(e):
                raise e

            breadcrumbs.record(data={'action': f'Exception: {datetime.now()}'}, category='info')
            logger = logging.getLogger()
            logger.info(f'Got telegram exception waiting 4 secs.')
            logger.info(e)
            if config.DEBUG:
                sentry.captureException()
            time.sleep(4)
            _try += 1

            exception = e
            pass

    raise exception
