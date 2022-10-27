"""Compilation of vote texts for each option."""
from typing import Any, List, Optional, Union

from sqlalchemy import func
from sqlalchemy.orm.scoping import scoped_session

from pollbot.display.poll import Context
from pollbot.enums import PollType
from pollbot.i18n import i18n
from pollbot.models import Option, Poll, User, Vote
from pollbot.poll.helper import (
    calculate_total_votes,
    poll_allows_cumulative_votes,
    poll_allows_multiple_votes,
)
from pollbot.poll.vote import get_sorted_doodle_votes, get_sorted_votes


def get_doodle_vote_lines(poll: Poll, option: Option, summarize: bool) -> List[str]:
    """Return all vote related lines for this option."""
    lines = []
    votes_by_answer = get_sorted_doodle_votes(poll, option.votes)

    # Do some super summarization in case the poll gets too long
    if summarize:
        for index, answer in enumerate(votes_by_answer.keys()):
            is_last = index == len(votes_by_answer.keys()) - 1
            line = i18n.t(
                f"poll.doodle.{answer}_summarized",
                locale=poll.locale,
                count=len(votes_by_answer[answer]),
            )

            # Last line must be properly styled
            if is_last:
                line = line.replace("├", "└")

            lines.append(line)

        return lines

    # Create the default or simple summarized vote lines
    for index, answer in enumerate(votes_by_answer.keys()):
        is_last = index == len(votes_by_answer.keys()) - 1
        lines.append(i18n.t(f"poll.doodle.{answer}", locale=poll.locale))
        lines += get_doodle_answer_lines(votes_by_answer[answer], summarize, is_last)
        if not is_last:
            lines += "┆"

    return lines


def get_doodle_answer_lines(
    votes: List[Vote], summarize: bool, is_last: bool
) -> List[str]:
    """Return the user names for a doodle answer.

    Try to compress as many usernames as possible into a single line.

    e.g.:
    Arne, Test1, Test2, Test3,
    wtfoktesttesthey, Test4, Test5,
    rofl, ...
    """
    threshold = 30
    votes_displayed = 0
    lines = []
    current_line = "┆ "
    characters = len(current_line)
    for index, vote in enumerate(votes):
        name_length = len(vote.user.name)

        # Only the characters of the username count (not the mention)
        characters += name_length
        # If the line lenght is above the threshold, start a new line
        # Don't stop here, if the first name of the line already is too long
        if characters > threshold and (2 + name_length) != characters:
            lines.append(current_line)
            current_line = "┆ "
            characters = len(current_line)

        user_mention = f"[{vote.user.name}](tg://user?id={vote.user.id})"
        # Add a comma at the end of the user mention if it's not the last one
        if index != (len(votes) - 1):
            user_mention += ", "

        current_line += user_mention
        votes_displayed += 1

    # Add the last line.
    # Replace the start character of the first line, to keep the styling correct
    if is_last:
        current_line = current_line.replace("┆", "└")
    lines.append(current_line)

    return lines


def get_vote_lines(poll: Poll, option: Option, summarize: bool) -> List[str]:
    """Return all vote related lines for this option."""
    lines = []
    threshold = 2
    # Sort the votes accordingly to the poll's settings
    votes = get_sorted_votes(poll, option.votes)
    for index, vote in enumerate(votes):
        # If we need to summarize the votes, just display the first few names
        # and summarize all remaining votes in a single line.
        if summarize and index == threshold:
            count = len(option.votes) - threshold
            lines.append(
                "└ " + i18n.t("poll.summarized_users", locale=poll.locale, count=count)
            )
            break

        vote_line = get_vote_line(poll, option, vote, index)
        lines.append(vote_line)

    return lines


def get_vote_line(poll: Poll, option: Option, vote: Vote, index: int) -> str:
    """Get the line showing an actual vote."""
    user_mention = f"[{vote.user.name}](tg://user?id={vote.user.id})"

    if index == (len(option.votes) - 1):
        vote_line = f"└ {user_mention}"
    else:
        vote_line = f"├ {user_mention}"

    if poll_allows_cumulative_votes(poll):
        vote_line += f" ({vote.vote_count} votes)"
    elif poll.poll_type == PollType.doodle.name:
        vote_line += f" ({vote.type})"

    return vote_line


def get_vote_information_line(poll: Poll, context: Context) -> Optional[str]:
    """Get line that shows information about total user votes."""
    vote_information = None
    if context.total_user_count > 1:
        vote_information = i18n.t(
            "poll.many_users_voted", locale=poll.locale, count=context.total_user_count
        )
    elif context.total_user_count == 1:
        vote_information = i18n.t("poll.one_user_voted", locale=poll.locale)

    if vote_information is not None and poll_allows_multiple_votes(poll):
        total_count = calculate_total_votes(poll)
        vote_information += i18n.t(
            "poll.total_votes", locale=poll.locale, count=total_count
        )

    return vote_information


def get_remaining_votes_lines(
    session: scoped_session, poll: Poll
) -> List[Union[str, Any]]:
    """Get the remaining votes for a poll."""
    user_vote_count = func.sum(Vote.vote_count).label("user_vote_count")
    remaining_user_votes = (
        session.query(User.name, user_vote_count)
        .join(Vote)
        .filter(Vote.poll == poll)
        .group_by(User.name)
        .having(user_vote_count < poll.number_of_votes)
        .order_by(User.name)
        .all()
    )

    if len(remaining_user_votes) == 0:
        return []

    lines = []
    lines.append(i18n.t("poll.remaining_votes", locale=poll.locale))
    for user_votes in remaining_user_votes:
        lines.append(
            i18n.t(
                "poll.remaining_votes_user",
                locale=poll.locale,
                name=user_votes[0],
                count=poll.number_of_votes - user_votes[1],
            )
        )

    return lines
