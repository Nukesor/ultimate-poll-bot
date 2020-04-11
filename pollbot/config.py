"""Config values for pollbot."""
import os
import sys
import toml
import logging

default_config = {
    'telegram': {
        "bot_name": 'your_bot_@_username',
        "api_key": "your_telegram_api_key",
        "worker_count": 20,
        "admin": 'nukesor',
        "allow_private_vote": False,
        "max_inline_shares": 20,
    },
    'database': {
        "sql_uri": 'postgres://localhost/pollbot',
        "connection_count": 20,
        "overflow_count": 10,
    },
    'logging': {
        "sentry_enabled": False,
        "sentry_token": "",
        "log_level": logging.INFO,
        "debug": False,
    },
    'webhook': {
        "enabled": False,
        "domain": "https://localhost",
        "token": "pollbot",
        "cert_path": '/path/to/cert.pem',
        "port": 7000,
    }
}

config_path = os.path.expanduser('~/.config/ultimate_pollbot.toml')

if not os.path.exists(config_path):
    with open(config_path, "w") as file_descriptor:
        toml.dump(default_config, file_descriptor)
    print("Please adjust the configuration file at '~/.config/ultimate_pollbot.toml'")
    sys.exit(1)
else:
    config = toml.load(config_path)
