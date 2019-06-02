"""Some static stuff or helper functions."""
from .enums import VoteType


donations_text = """
Hello there!

My name is Arne Beer (@Nukesor) and I'm the sole developer of the Ultimate PollBot.

The whole project has been created during my leisure time and for free.
This project is non-profit, open-source on [Github](https://github.com/Nukesor/pollbot) and hosted on a server I'm renting from my own money.

I really appreciate anything that helps me out and that keeps me and my server running ☺️.

If you like this project, check my [Patreon](https://www.patreon.com/nukesor) or support me via [Paypal](https://www.paypal.me/arnebeer).

Have great day!
"""


start_text = """*Hi!*

This is the *ULTIMATE* pollbot.
Just type /create or click the button below to start creating polls. Everything is explained underway.

This project is open-source and hosted on [Github](https://github.com/Nukesor/ultimate-poll-bot).
"""


error_text = """An unknown error occurred. I probably just got a notification about this and I'll try to fix it as quickly as possible.
In case this error still occurs in a day or two, please report the bug to me :). The link to the Github repository is in the /start text.
"""


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


def poll_is_cumulative(poll):
    """Check whether this poll's type is cumulative."""
    return poll.vote_type == VoteType.cumulative_vote.name


def calculate_total_votes(poll):
    """Calculate the total number of votes of a poll."""
    total = 0
    for vote in poll.votes:
        total += vote.vote_count

    return total
