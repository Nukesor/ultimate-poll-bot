"""Some static stuff or helper functions."""
from .enums import VoteType


donations_text = """
Hello there!

My name is Arne Beer (@Nukesor) and I'm the sole developer of the Ultimate PollBot.

The idea of writing the Ultimate Pollbot was formed, when my friends couldn't decide again where we should go for lunch.
This happened so many times already and we desperately needed a good and stable solution inside of telegram for this problem!
That's how the ULTIMATE Pollbot was born.

Every line of code in this project was written in my leisure time and is completely for free.
This project is non-profit, open-source on [Github](https://github.com/Nukesor/ultimate-poll-bot) and hosted on a server I'm renting from my own money.

Right now I usually invest between 2-10 hours a week into developing and maintaining my projects and I would love to get some support, since I'm doing this in a large part for you out there.

I really appreciate anything that helps me out and that keeps my server and me running ☺️.

If you like this project, check my [Patreon](https://www.patreon.com/nukesor) or support me via [Paypal](https://www.paypal.me/arnebeer).

Have great day!
"""


start_text = """*Hi!*

This is the *ULTIMATE* pollbot.
Just type /create or click the button below to start creating polls. Everything is explained underway.

If you have more questions, check out /help.

This project is open-source on [Github](https://github.com/Nukesor/ultimate-poll-bot).
"""

help_text = """There are quite a few settings for your polls:

*Creation:*
1. You can anonymize your poll, which results in no names being displayed!
2. Poll results can be shown only after closing the poll. This is great to avoid tactical voting, which is possible if people can see the intermediate results of a poll.

*Settings:*
1. A poll can be made anonymous retrospectively.
2. The percentage line of options can be hidden in the settings menu.
3. New options can be added and existing options can be removed in the settings menu.
4. You can allow other users to add options to your poll.
5. The order in which user names and options are displayed in the results can be changed.

*Notifications:*
To enable notifications in a chat follow these steps:
1. Create a poll
2. Set a due date in the settings menu
3. Go to the chat you want to be notified (The pollbot needs added to the group)
4. Reply with /notify to the poll message you forwarded
5. Pick the correct poll

This whole procedure is unhappily overly complicated, since telegram doesn't allow to detect forwarded messages from bots in groups.
Thereby we don't know which poll is posted in which group and everything needs to be done manually.

*Find old polls:*
There are two commands `/list` and `/list\_closed`, which allow you to find and manage your old polls.

*Delete polls*
You can delete individual polls in the respective poll menus.
There's also the /delete\_closed command, which deletes all closed polls
and the /delete\_all command which deletes ALL polls.

*Too many votes in the last minute:*
Don't worry about this message. This mechanism is necessary to prevent my bot from being blocked by telegram for spamming messages.
The only effect for you is, that the results won't be displayed immediately.

*My polls won't update:*
In this case you probably have multiple active polls in a single group (or the same poll multiple times).
This is something the bot cannot detect (telegrams API doesn't allow this). Therefore you need to handle this yourself.
Only have one highly active poll per group and don't send the same poll multiple times in the same group (or delete the old ones for ALL members of the group).

*There is a bug that won't go away!!*
I usually get a notification as soon as something breaks, but there might be some bugs that go unnoticed!
In case a bug isn't fixed in a day or two, please write a ticket on [Github](https://github.com/Nukesor/ultimate-poll-bot).
"""


error_text = """An unknown error occurred. I probably just got a notification about this and I'll try to fix it as quickly as possible.
In case this error still occurs in a day or two, please report the bug to me :). The link to the Github repository is in the /start text.
"""

first_option_text = """Please send me an option. You can send multiple options at once, each option on a new line.
You can also add a description behind a hyphen.
For instance `Burger - because it is tasty`
"""


def poll_required(function):
    """Decorator that just returns if the poll is missing."""
    def wrapper(session, context):
        if context.poll is None:
            return

        function(session, context, context.poll)

    return wrapper


def poll_allows_multiple_votes(poll):
    """Check whether the poll allows multiple votes."""
    multiple_vote_types = [
        VoteType.block_vote.name,
        VoteType.limited_vote.name,
        VoteType.cumulative_vote.name,
    ]

    return poll.vote_type in multiple_vote_types


def poll_has_limited_votes(poll):
    """Check whether the poll has limited votes."""
    vote_type_with_vote_count = [
        VoteType.limited_vote.name,
        VoteType.cumulative_vote.name,
    ]

    return poll.vote_type in vote_type_with_vote_count


def poll_allows_cumulative_votes(poll):
    """Check whether this poll's type is cumulative."""
    return poll.vote_type in [
        VoteType.cumulative_vote.name,
        VoteType.count_vote.name
    ]


def calculate_total_votes(poll):
    """Calculate the total number of votes of a poll."""
    total = 0
    for vote in poll.votes:
        total += vote.vote_count

    return total
