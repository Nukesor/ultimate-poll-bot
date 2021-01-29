# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0]

### Changed

- Wait for a longer time after flood control exceptions in the delete logic.
    This makes the whole process more resilient.
- Move the whole poll deletion logic to an asynchronous background job.
- Black code styling
- Fix some weird issue that's probably related to Telegram's internal syncing when handling inline query results
- Add client-side rate-limiting for errors to prevent flooding Sentry.
- General dependency update.

### Added

- Users can retry to update references via button click.

### Fixed

- Fixed race-conditions that were created due to asynchronous poll deletion.
- Some race-condition exception handling
- Fix statistic plotting related memory leak
- Handle a lot of edge-case exceptions that can be ignored.
- Fix some unhandled markdown characters in usernames

## [1.6.0] - 2020-08-09

### Added

- Pagination when listing polls.

### Changed

- Users are only allowed to own 200 polls (by default).
- Poll Messages won't be removed when deleting all/all closed polls.
- Use local venv for development with poetry
- Dependency updates

**Internal:**

- Huge internal restructuring and refactoring
- Updated from `raven` to `sentry-sdk`

### Fixed

- Broken polls after adding new options to Priority Poll.
- Fixed broken poll creation, when users added too many options at once.
- Fixed exceptions when the bot was used in groups he wasn't allowed to send messages.
- Fixed broken `/list` and `/list_closed` for users with too many polls
- Fixed exceptions due to duplicate inline result updates.
- Fixed exceptions due to channel posts in message handlers
- Ignored exceptions when `/start` commands came in without a message.
- Fixed broken polls due to special characters in usernames and poll names/titles

## [1.5.0] - 2020-07-08

### Added

- Create new polls from native Telegram Polls. Thanks to [@Josxa](https://github.com/josxa)
- Add complete deletion of all user data
- Support `/stop`

### Changed

- Streamline poll styling interface
- Added feature request tab in `/help`

**Internal:**

- Fixe race-condition database bugs by running certain callback handlers synchronous
- Add a contribution guide
- New sentry sdk
- Code formatting with black
- Cleanup session handling

### Fixed

- Option with empty names can be fixed
- Handle `/start` messages without a message
- Handle polls that have too many options during creation
- Fix a bug where inline message references could be duplicated

## [1.4.0] - 2020-04-29

### Added

- Options can be sorted manually
- New options. You have need to add those your config manually if you already have a deployed bot:
    1. `telegram.max_inline_shares` The max amount of shared messages via inline query per poll
    2. `telegram.allow_private_vote` This decides, whether you allowed 
    3. `telegram.max_user_votes_per_day` Set a limit how many votes are allowed per user per day.

### Changed

- Add anti-spam measures
- Add possibility to ban users
- Temporarily ban users on certain thresholds
- Catalan language

**Internal:**

- Configurable amount for max shared messages via inline query per poll
- Slow async background updating of poll in other chats, while instantly updating the message the user voted on.
- Removal of duplicate poll messages in private chats

## [1.3.0] - 2020-02-11

### Added

- Priority vote poll. Thanks to [Raffomania](https://github.com/raffomania) and [hatzel](https://github.com/hatzel)!
- Streamline all datepickers (breaking changes)
- Display week day in vote buttons
- Add explanations for most important options
- Add warning about possible information leak via online status on anonymous polls
- Add option to hide option count on polls.
- Add option to allow/forbid sharing of polls

- Language updates
- Improvement of internal error handling

### Fixed

- Fixed poll notifications and due dates
- Numerous minor bug fixes
- Fix some security issues which allowed adding and sharing polls without explicit permission


## [1.2.0] - 2019-11-07

### Added

- Completely revamp the user settings and /start interface
- Add /settings command as shortcut to settings submenu
- Add a prompt when deleting all polls of a user
- Option to delete a specific poll without removing all messages
- Link in poll settings, which allows anybody to share this poll to arbitrary groups
- New doodle button layout. Old one can still be selected in poll styling settings

- Lokalise integration
- New language Italian
- New language Spanish
- New language Portuguese (Brazil)
- New language Czech
- Text adjustments
- Forbid polls which are longer than 4000 characters at point of creation (Telegram limit)
- Send warning for polls which are longer than 3000 characters at point of creation

### Fixed
- Hide remaining votes in anonymous polls
- Fixed a bug where messages couldn't be sent due to messages being too long
- Fixed a bug where inline queries didn't work due to many very long polls.
- Percentage order option removed for doodle

## [1.1.0] - 

### Added

- Support for super long polls. Those polls now get summarized as soon as they reach a certain length and a new button appears.
    This button redirects to the bot and gives you a detailed summary of the poll results in multiple messages. (Telegram only allows 4096 characters per message)
- Clicking on the letter buttons on a doodle poll (`a)`, etc.) now shows the option's name
- Revamp of the doodle result interface
- Better help interface
- Lots of text adjustments
- Share polls after they have been closed
- New language: Polish (Thanks to tszalbot)

**New styling menu:**

- All styling and sorting related setting were put into a dedicated styling menu
- All impacts on the poll layout can be seen live in the message above
- Added new summarization setting. (Options with many votes are summarized like this and 10 oher people)

### Fixed

- Fixed a bug, where votes weren't registered, because the option name was too long.
- Fixed a bug, where a user could vote twice on a single vote poll.
- Fixed a bug, where a user could get a deleted poll in inline queries due to caching
- Fixed a bug, where notifications weren't sent for all users due to one single user activating notifications and then removing the bot from the group.
- Fixed a bug, where notifications weren't working, if the due date was more then 1 week in the future.
- Hide remaining votes for unlimited poll

## v1.0.1

### Added

- New language: German
- New language: Turkish (Thanks to @cnpltdncsln)
- Users in polls are linked with telegram mentions

### Fixed

- Prevent usage of markdown characters in user input
- Fixed many typos/wrong translation keys
- Fixed datepicker behaviour (Was really fucky before)
- Some minor bugs

## v1.0.0

### Added

- Support for super long polls. Those polls now get summarized as soon as they reach a certain length and a new button appears.
    This button redirects to the bot and gives you a detailed summary of the poll results in multiple messages. (Telegram only allows 4096 characters per message)
- Clicking on the letter buttons on a doodle poll (`a)`, etc.) now shows the option's name
- Revamp of the doodle result interface
- Better help interface
- Lots of text adjustments
- Share polls after they have been closed
- New language: Polish (Thanks to tszalbot)

**New styling menu:**

- All styling and sorting related setting were put into a dedicated styling menu
- All impacts on the poll layout can be seen live in the message above
- Added new summariza
- New poll type - the shopping list
- New poll type - doodle (yes, no, maybe)
- Set a due date for a poll, at which the poll will be automatically closed
- Activate notifications in chats, which remind everyone that the poll will close soon
- Addition and removal of options
- Introduce setting which allows all users to add options 
- Clone and Resetting of polls

- Datepicker for options
- External users can use the datepicker, when adding new options
- Complete redesign of the poll interface
- Better poll management interface structure
- Allow european date formatting (This will be remembered for future polls)

### Fixes
- A good amount of bugfixes
