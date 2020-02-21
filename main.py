#!/bin/env python
"""Start the bot."""
from pollbot.pollbot import client

with client:
    client.run_until_disconnected()
