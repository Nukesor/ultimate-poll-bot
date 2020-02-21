"""Config values for pollbot."""
import os
import sys
import toml
import logging

default_config = {
    'telegram': {
        "bot_name": 'your_bot_username(without the @)',
        "bot_token": "your_botfather_token",
        "api_id": "my.telegram.org_api_id",
        "api_hash": "my.telegram.org_api_hash",
        "admin": 'nukesor',
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
}

config_path = os.path.expanduser('~/.config/ultimate_pollbot.toml')

if not os.path.exists(config_path):
    with open(config_path, "w") as file_descriptor:
        toml.dump(default_config, file_descriptor)
    print("Please adjust the configuration file at '~/.config/ultimate_pollbot.toml'")
    sys.exit(1)
else:
    config = toml.load(config_path)
