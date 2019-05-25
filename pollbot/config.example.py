"""Config values for pollbot."""
import logging


class Config:
    """Config class for convenient configuration."""

    # Get your telegram api-key from @botfather
    TELEGRAM_API_KEY = None
    SQL_URI = "postgres://localhost/pollbot"
    SENTRY_TOKEN = None
    LOG_LEVEL = logging.INFO

    # Username of the admin
    ADMIN = 'Nukesor'
    # Check whether the bot instance should only listen to chats and collect stickers
    LEECHER = False
    # Only important if running multiple instances ( for logging )
    BOT_NAME = 'pollbot'

    # Use and configure nginx webhooks
    WEB_HOOK = False
    DOMAIN = 'https://example.com'
    TOKEN = 'token'
    CERT_PATH = './cert.pem'
    PORT = 5000

    # Performance/thread/db settings
    WORKER_COUNT = 16
    CONNECTION_COUNT = 20
    OVERFLOW_COUNT = 10

    # Job parameter
    USER_CHECK_COUNT = 200
    REPORT_COUNT = 1


config = Config()
