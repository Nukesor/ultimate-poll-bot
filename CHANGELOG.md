## v1.3.0
- Priority vote poll
- Streamline all datepickers (breaking changes)
- Display week day in vote buttons
- Add explanations for most important options
- Add warning about possible information leak via online status on anonymous polls
- Add option to hide option count on polls.

- Language updates
- Improvement of internal error handling

**Fixes:**
- Fixed poll notifications and due dates
- Numerous minor bug fixes


## v1.2.0
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

**Fixes:**
- Hide remaining votes in anonymous polls
- Fixed a bug where messages couldn't be sent due to messages being too long
- Fixed a bug where inline queries didn't work due to many very long polls.
- Percentage order option removed for doodle

## v1.1.0
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

**Fixes:**
- Fixed a bug, where votes weren't registered, because the option name was too long.
- Fixed a bug, where a user could vote twice on a single vote poll.
- Fixed a bug, where a user could get a deleted poll in inline queries due to caching
- Fixed a bug, where notifications weren't sent for all users due to one single user activating notifications and then removing the bot from the group.
- Fixed a bug, where notifications weren't working, if the due date was more then 1 week in the future.
- Hide remaining votes for unlimited poll

## v1.0.1
**Additions:**
- New language: German
- New language: Turkish (Thanks to @cnpltdncsln)
- Users in polls are linked with telegram mentions

**Fixes:**
- Prevent usage of markdown characters in user input
- Fixed many typos/wrong translation keys
- Fixed datepicker behaviour (Was really fucky before)
- Some minor bugs

## v1.0.0

**Additions:**
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


**Maintenance:**
- A good amount of bugfixes
