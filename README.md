# Ultimate Pollbot ([@ultimate_pollbot](https://t.me/ultimate_pollbot))


[![MIT Licence](https://img.shields.io/badge/license-MIT-success.svg)](https://github.com/Nukesor/pollbot/blob/master/LICENSE.md)
[![Paypal](https://github.com/Nukesor/images/blob/master/paypal-donate-blue.svg)](https://www.paypal.me/arnebeer/)
[![Patreon](https://github.com/Nukesor/images/blob/master/patreon-donate-blue.svg)](https://www.patreon.com/nukesor)


![Alt Text](https://github.com/Nukesor/images/blob/master/pollbot.gif)

Deciding where you and your friends are going for lunch today can be a real hassle...
Or, for instance, deciding which games should be played at the next LAN-Party.

Since no other telegram poll-/votebot offered the full feature set my friends and I needed, I decided to write the ULTIMATE pollbot. A bot which combines all good features of all existing bots and even stuff beyond that.


## Features:
There are still some features missing, such as Deadlines, Notifications and even more Vote types, but in my opinion it's already better than anything I could find out there.


**Poll types**

This bot has 5 different vote modi. Each mode is useful for various scenarious. Choose wisely.

- Single vote: User get a single vote to allot
- Doodle: Users can vote with `yes`, `no` and `maybe` for each option.
- Block vote: Users can vote without restriction, but only one vote per option.
- Limited vote: Each user gets X votes for distribution, but only one vote per option.
- Cumulative vote: Every user gets X votes they can distribute as they like.
- Unlimited votes (Also called the shopping list): Every user can vote as often as they like, pretty much like a distributed shopping list.

**Anonymity settings:**

Polls can be configured to be anonymous, with the result that names of users are not visible.
Polls can be made anonymous subsequently, but as soon as a poll is anonymous it stays that way forever!

Further it's possible to hide the results of the poll until it gets closed.
As soon as such a poll is closed, the results will be visible. **Beware!**: such an poll cannot be reopened.

**Poll Management:**
- Addition and removal of options
- Allow other users to add new options
- Polls can be closed
- Polls can be reopened unless the poll is configured to hide the results until it has been closed.
- Polls can be completely deleted, which means that all non-forwarded occurences of the poll will be removed.
- Polls can be resetted (Delete all votes). Poll needs to be closed first
- Polls can be cloned (New poll with same options, but without votes). Poll needs to be closed first


**Convenience features:**
- A datepicker for easier creation of poll options
- Specify a due date, at which the poll will be automatically closed.
- Activate notifications in chats to notify users that the poll will close soon.


**Sorting and Appearance:**

- The percentage bar in the vote message can be disabled.
- The bot allows to configure the sorting of the option list AND and the user list for each option.
- Users can be sorted by vote date or username. Options can be sorted by highest percentage, name or by the order they've been added.


**Flood controll prevention:**

Telegram forbids to send more than a certain amount of messages per minute into the same group. This obviously leads to problems, if there are many people that vote on a single poll.

Pollbot has a proper way of handling this problem.
In case you hit a certain amount of votes for the current minute, the bot will stop updating the messages on each vote, but it will rather update all messages every five seconds.
Votes will still be registered and you'll get feedback via button callback notification.
With this mechanism you can keep spamming vote buttons and do as you like without crashing the bot or activating flood control limits.


**Planned features:**

- A doodle poll
- A STV poll


## Commands:

    /start          Start the bot
    /create         Create a new poll
    /list           List all active polls and manage them
    /list_closed    List all closed polls and manage them
    /delete_closed  Delete all closed polls
    /delete_all     Delete all polls (closed and unclosed)
    /help           Display the help
    /donations      Get me a coffee


## Installation and Starting:
**This bot is developed for Linux.** Windows isn't tested, but it shouldn't be too hard to make it compatible. Feel free to create a PR.

Dependencies: 
- `poetry` to manage and install dependencies.
- Ultimate Pollbot uses postgres by default. Make sure the user has write/read rights. (This can be changed, by changing the SQLURI in the configuration file.)


1. Clone the repository:

        % git clone git@github.com:nukesor/ultimate_pollbot pollbot && cd pollbot

2. Execute following commands to install all dependencies and to initialize the database:

        % poetry install
        % poetry run initdb.py

3. Either start the pollbot once or copy the `ultimate_pollbot.toml` manually to `~/.config/ultimate_pollbot.toml` and adjust all necessary values.
4. Start the bot `poetry run main.py`

5. If you plan to keep up to date, you need to set the current alemibic revision manually.
Get the latest revision with `poetry run alembic history` and change the current head to the newest revision with `poetry run alembic stamp <revision>`.
6. Now you can just execute `poetry run alembic upgrade head`, whenever you are updating from a previous version.



## Botfather Commands

start - Start the bot
create - Create a new poll
language - Change the language
list - List all active polls and manage them
list_closed - List all closed polls and manage them
delete_closed - Delete all closed polls
delete_all - Delete all polls (closed and unclosed)
help - Show the help text
donations - Get me a coffee
