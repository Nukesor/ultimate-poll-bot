"""Simple wrapper around sentry that allows for lazy initilization."""
import sentry_sdk
from sentry_sdk import configure_scope

from pollbot.config import config
from telegram.error import TimedOut


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


sentry = Sentry()
