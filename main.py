#!/bin/env python
"""Start the bot."""

from pollbot.pollbot import updater
from pollbot.config import config

if config.WEB_HOOK:
    updater.start_webhook(listen='127.0.0.1', port=config.PORT, url_path=config.TOKEN)
    updater.bot.set_webhook(url=f'{config.DOMAIN}{config.TOKEN}',
                            certificate=open(config.CERT_PATH, 'rb'))
else:
    updater.start_polling()
    updater.idle()
