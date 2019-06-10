"""Config values for pollbot."""
import logging


class Config:
    """Config class for convenient configuration."""

    # Get your telegram api-key from @botfather
    TELEGRAM_API_KEY = None
    SQL_URI = 'postgres://localhost/pollbot'
    SENTRY_TOKEN = None
    LOG_LEVEL = logging.INFO

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

    # Flood limit parameter
    FLOOD_THRESHOLD = 8


config = Config()
