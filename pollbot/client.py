import asyncio
from telethon import TelegramClient
from pollbot.config import config

loop = asyncio.get_event_loop()
client = TelegramClient(
    config['telegram']['bot_name'],
    config['telegram']['api_id'],
    config['telegram']['api_hash'],
    loop=loop
)
client.start(bot_token=config['telegram']['bot_token'])

# Connect once and cache the current id
# We need this in pretty much every request
client_id = 0
with client:
    me = client.loop.run_until_complete(client.get_me())
    client_id = me.id
