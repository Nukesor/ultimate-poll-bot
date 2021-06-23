"""Simple wrapper around sentry that allows for lazy initilization."""
import traceback

import sentry_sdk
from sentry_sdk import configure_scope
from telegram.error import NetworkError, TimedOut

from pollbot.config import config


def ignore_job_exception(exception):
    """Check whether we can safely ignore this exception."""
    if type(exception) is TimedOut:
        return True

    # Super low level http error
    if type(exception) is NetworkError:
        return True

    return False


class Sentry(object):
    """Sentry wrapper class.

    This class offers some convenience classes and functions for adding
    additional information to sentry calls.

    The extra level of abstraction ensures that everything will still work,
    if sentry hasn't been initialized.
    """

    initialized = False

    def __init__(self):
        """Construct new sentry wrapper."""
        if config["logging"]["sentry_enabled"]:
            self.initialized = True
            sentry_sdk.init(
                config["logging"]["sentry_token"],
            )

    def capture_message(self, message, level="info", tags=None, extra=None):
        """Capture message with sentry."""
        if not self.initialized:
            return

        with configure_scope() as scope:
            if tags is not None:
                for key, tag in tags.items():
                    scope.set_tag(key, tag)

            if extra is not None:
                for key, extra in extra.items():
                    scope.set_extra(key, extra)

            scope.set_tag("bot", "pollbot")
            sentry_sdk.capture_message(message, level)

    def capture_exception(self, tags=None, extra=None):
        """Capture exception with sentry."""
        if not self.initialized:
            return

        with configure_scope() as scope:
            if tags is not None:
                for key, tag in tags.items():
                    scope.set_tag(key, tag)

            if extra is not None:
                for key, extra in extra.items():
                    scope.set_extra(key, extra)

            scope.set_tag("bot", "pollbot")
            sentry_sdk.capture_exception()

    def capture_job_exception(self, exception):
        # Capture all exceptions from jobs. We need to handle those inside the jobs
        if not ignore_job_exception(exception):
            if config["logging"]["debug"]:
                traceback.print_exc()

            sentry.capture_exception(tags={"handler": "job"})


sentry = Sentry()
