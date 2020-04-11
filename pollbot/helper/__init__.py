"""Some static stuff or helper functions."""
from pollbot.config import config


def get_escaped_bot_name():
    """Get the bot name escaped for markdown."""
    name = config["telegram"]["bot_name"]
    escaped = name.replace("_", "\_")

    return escaped
