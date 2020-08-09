"""Some static stuff or helper functions."""
from pollbot.config import config

markdown_characters = ["[", "`", "*", "_", "`"]

translation_table = dict.fromkeys(map(ord, "".join(markdown_characters)), None)


def get_escaped_bot_name():
    """Get the bot name escaped for markdown."""
    name = config["telegram"]["bot_name"]
    escaped = name.replace("_", "\_")

    return escaped


def remove_markdown_characters(string):
    """Remove all markdown symbols from the string."""
    removed = string.translate(translation_table)
    return removed
