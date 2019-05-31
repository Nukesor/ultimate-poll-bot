# Ultimate Pollbot ([@ultimate_pollbot](https://t.me/ultimate_pollbot))

[![MIT Licence](https://img.shields.io/badge/license-MIT-success.svg)](https://github.com/Nukesor/pollbot/blob/master/LICENSE.md)
[![Paypal](https://github.com/Nukesor/images/blob/master/paypal-donate-blue.svg)](https://www.paypal.me/arnebeer/)
[![Patreon](https://github.com/Nukesor/images/blob/master/patreon-donate-blue.svg)](https://www.patreon.com/nukesor)


# Features

- This bot has 4 different vote modi.
    1. Single vote: User get one vote for the poll
    2. Block vote: Users can vote without restriction, but only one vote per option.
    3. Limited vote: Each user gets X votes for distribution, but max one vote per option.
    4. Election vote: Every user gets X votes they can distribute as they like.

- Custom sorting of options and users
- Anonymize a poll subsequently
- Set a due date for a poll (Not yet)
- Get due date notifications for polls, if the bot is in the same group (Not yet)
- You get a date picker (Not yet)


## Commands:

    /start      Start the bot
    /create     Create a new poll
    /list       List all active polls and manage them
    /help       Display help
    /donations  Get me a coffee


## Installation and starting:

1. You will need to install `poetry` to install all dependencies.
2. Clone the repository:

        % git clone git@github.com:nukesor/ultimate_pollbot pollbot && cd pollbot

3. Now copy the `pollbot/config.example.py` to `pollbot/config.py` and adjust all necessary values.
4. Finally execute following commands to install all dependencies and to start the bot:

        % poetry install
        % poetry run initdb.py
        % poetry run main.py

5. If you plan to keep up to date, you need to set the current alemibic revision manually.
Get the latest revision with `poetry run alembic history` and change the current head to the newest revision with `poetry run alembic stamp <revision>`.
6. Now you can just execute `poetry run alembic upgrade head`, whenever you are updating from a previous version.



## Botfather commands

    start - Start the bot
    create - Create a new poll
    list - List all active polls and manage them
    help - Display help
    donations - Get me a coffee
