#!/bin/env python
"""Start the bot."""

from pollbot.pollbot import updater
from pollbot.config import config

if config["webhook"]["enabled"]:
    domain = config["webhook"]["domain"]
    token = config["webhook"]["token"]
    updater.start_webhook(
        listen="127.0.0.1",
        port=config["webhook"]["port"],
        url_path=config["webhook"]["token"],
    )
    updater.bot.set_webhook(
        url=f"{domain}{token}", certificate=open(config["webhook"]["cert_path"], "rb")
    )
else:
    updater.start_polling()
    updater.idle()
