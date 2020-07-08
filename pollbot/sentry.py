"""Simple wrapper around sentry that allows for lazy initilization."""
import sentry_sdk
from pollbot.config import config
from telegram.error import TimedOut


class Sentry(object):
    """Sentry wrapper class that allows this app to work without a sentry token.

    If no token is specified in the config, the messages used for logging are simply not called.
    """

    initialized = False

    def __init__(self):
        """Construct new sentry wrapper."""
        if config["logging"]["sentry_enabled"]:
            self.initialized = True
            sentry_sdk.init(config["logging"]["sentry_token"],)
            self.sentry = sentry_sdk

    def capture_message(self, *args, **kwargs):
        """Capture message with sentry."""
        if self.initialized:
            if "tags" not in kwargs:
                kwargs["tags"] = {}

            # Tag it as pollbot
            kwargs["tags"]["bot"] = "pollbot"
            self.sentry.capture_message(*args, **kwargs)

    def capture_exception(self, *args, **kwargs):
        """Capture exception with sentry."""
        if self.initialized:
            if "tags" not in kwargs:
                kwargs["tags"] = {}

            # Tag it as pollbot
            kwargs["tags"]["bot"] = "pollbot"
            self.sentry.capture_exception(*args, **kwargs)


sentry = Sentry()
