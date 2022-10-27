# Hi!

This document is supposed to give you a short introduction to the project.

It's purpose is to explain the project structure, so you understand where you can find the parts of code you're looking for.

## Prerequisites

### Python Telegram Bot

Ultimate Poll Bot is based on the Python Telegram Bot library! Please read the docs and familiarize yourself with the library.
You can find a nice introduction and basic information on how to use it over [here](https://python-telegram-bot.org/).
On top of that, there are very detailed [api docs](https://python-telegram-bot.readthedocs.io/en/stable/).

### Sqlalchemy

The database integration for this project is written with [SQLAlchemy](https://www.sqlalchemy.org/).
In detail, the project uses the [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/13/orm/) abstraction layer.

Please familiarize yourself with the basic SQLAlchemy ORM syntax and SQL in general.

### Alembic

For database migrations, we use [Alembic](https://alembic.sqlalchemy.org/en/latest/).
Alembic wraps around SQLAlchemy and is used to manage migrations and transition between versions.

It can also be used to auto-generate migrations, which is possible due to SQLAlchemy's nice ORM implementation.

### Postgres

There are a few Postgres-only features used in this project.
It may be possible to use it in combination with another database, but a few important features and safe-guards would be lost in the progress.
Thereby, this won't be added to the main project.

## Top level structure

- `bin` In here you can find a bunch of helper scripts for development.
        This can be ignored for the most part and isn't important for normal operation/development.
- `i18n` This is the local mirror for translations from localise.com.
        You don't need to touch it, unless you want to add new translation keys.
        In case you do, please add them to `English.yml` and add further translations via Lokalise.
- `migrations` All alembic migration files.
        Those are usually managed via the program `alembic` and can be generated automatically without any need for manual adjustments.
        Only create new migrations, if you have to change the database schema!
        Also read the Alembic documentation first, so you know how to do this.
- `pollbot` This is the source code of the project.
- `queries` Some helper queries. Nothing important and probably not interesting for you.
- `tests` Well, there was an attempt to test stuff. If you would like to add tests, please go ahead!! It's very much appreciated.

## The main source code structure

- `config.py` Configuration parsing and initialization.
- `db.py` Database initialization and session creation helper function.
- `i18n.py` Internationalization initialization.
- `sentry.py` Sentry initialization and a helper/wrapper class.
- `pollbot.py` The main file of the project. In here the Bot and **all** Handlers are initialized.
- `enums.py` All enums that are used in the project.

### display

This module is all about creating and formatting text. \
This includes various interfaces, such as settings, styling, etc. as well as the full logic for compiling poll texts. \
The stuff for compiling poll texts is contained in it's own submodule `display.poll`.

### helper

In here you can find a lot of small helper functions.
These include:

- Statistics
- I didn't know where else to put this stuff

### models

The folder for all SQLAlchemy ORM models.
Each file is dedicated to a single model.

This should be fairly straight forward.

### poll

Most of the logic for managing polls.
This includes:

- Poll update logic
- Poll remove logic
- Poll voting logic
- Sorting functions
- Helper functions for creating/managing polls
- Helper functions for adding/removing options

### telegram

Now we're getting to the juicy part.

- `inline_query.py` Everything that happens when an inline query with `@ultimate_pollbot word` is fired.
- `inline_result_handler.py` Everything that happens once somebody selects a result from an inline query response.
- `session.py` Wrappers for all telegram calls. Take a look at the _Session helper_ section for more information.

#### job.py

This is where all jobs are contained.
These include:

- Asynchronous updating of poll messages
- Sending of notifications
- Banning people
- Maintenance queries

#### message_handler.py

Handling of private text messages.

This isn't too much.
It's basically a single entry point, which interprets the given user input depending on the current `User.expected_input` state.

Look at the `enum.ExpectedInput` enum for all possible inputs.

Examples:

- Poll name, description, options etc.
- Added option by external user.
- Option added after poll has been created.

#### Keyboard

This folder is dedicated to helper functions for creating **all** keyboards used by the bot.

If you want to change a keyboard or add a new keyboard, please add it to the files in this folder.

#### Commands

In here you can find all direct command handlers. E.g. `/start` or `/create`.
This should be pretty straight forward.

#### Callback handler

Most interactions are done using buttons, that's why this probably contains most of the bot's logic.

In general, there are two entry points for callbacks in `callback_handler.__init__`:

- `handle_callback_query` This is used to run critical callbacks, that could lead to race-conditions.
    If you're doing critical stuff in the database, your call should be handled by this function.

- `handle_async_callback_query`, which is used to run non-critical callbacks.
    Anything that's not touching the database or does so in read-only mode, can be used with this.
    Voting is an edge-case, since this has to be async to prevent a bottle neck.
    Therefore, there's a lot of special exception handling in the whole voting logic.

To add a new function to either of those handlers, take a look at the `callback_handler.mapping` file.

In here, you can assign a CallbackType to a function.
Each button gets a payload with the default structure of e.g. `f"{{ CallbackType.vote.value }}:{{ poll.id }}:{{ CallbackResult.yes.value }}`.
After formatting, this might look like this `20:51203:21`.
Depending on the `CallbackType` in this payload, the respective handler will then call the respective function, just as specified in `callback_handler.mapping`.

`CallbackType` is expected in **EVERY** payload. Otherwise we won't be able to call the correct callback handling function.
The rest can be used arbitrarily, but the second argument is used for `poll.id` in most cases.

##### CallbackContext

This is a nice helper class that's passed into all callback functions.
It automatically parses the payload and tries to interpret:

- the first element as `CallbackType`
- the second argument as a `Poll`, which is then stored in `CallbackContext.poll`
- the third argument as `CallbackResult`

The second and third can fail.
If `CallbackType` is invalid, an exception will be thrown, since it's expected!

## Session helper

Take a look at `telegram.session`.

In here you can find convenience helper that are used around **EVERY** Telegram handler.

Their job is to do this:

- User initialization
- Database session initialization
- Exception handling and reporting
- Check whether users are allowed to use the bot

If you plan to create a new Telegram handler or if you want to handle some exceptions, please consider using or adjusting these session handlers.
