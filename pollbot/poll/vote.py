"""Helper functions for votes."""
import random
from typing import Dict, List

from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.scoping import scoped_session

from pollbot.enums import UserSorting
from pollbot.models import Option, Poll, User, Vote


def init_votes(session: scoped_session, poll: Poll, user: User) -> None:
    """
    Since Priority votes always need priorities, call this to create a vote
    for every option in the poll with a random priority for the given user.
    """
    assert poll.is_priority()

    # Don't init votes, if there already is a vote
    any_vote = (
        session.query(Vote).filter(Vote.user == user).filter(Vote.poll == poll).first()
    )
    if any_vote is not None:
        return

    votes = []
    for index, option in enumerate(random.sample(poll.options, len(poll.options))):
        vote = Vote(user, option)
        vote.priority = index
        votes.append(vote)
    session.add_all(votes)


def init_votes_for_new_options(
    session: scoped_session, poll: Poll, added_options: List[str]
) -> None:
    """
    When a new option is added, we need to create new votes
    for all users that have already voted for this poll.
    """
    if not poll.is_priority():
        return

    # Get all newly added options
    new_options = (
        session.query(Option)
        .filter(Option.poll == poll)
        .filter(Option.name.in_(added_options))
        .all()
    )

    # The new options are already flushed.
    # Subtract the amount of new options to get the proper index.
    existing_options_count = len(poll.options) - len(new_options)

    users_that_voted = (
        session.query(User).join(User.votes).filter(Vote.poll == poll).all()
    )

    for user in users_that_voted:
        for index, option in enumerate(new_options):
            vote = Vote(user, option)
            vote.priority = existing_options_count + index
            user.votes.append(vote)


def reorder_votes_after_option_delete(session, poll: Poll):
    """Reorders votes after the deletion of an option.

    When deleting an option from a poll, all existing votes need to be reordered.
    Otherwise there might be a gap between priorities of votes.
    """
    users = session.query(User).join(User.votes).filter(Vote.poll == poll).all()

    for user in users:
        votes = (
            session.query(Vote)
            .filter(Vote.poll == poll)
            .filter(Vote.user == user)
            .order_by(Vote.priority.asc())
            .all()
        )

        for index, vote in enumerate(votes):
            vote.priority = index
    session.flush()


def get_sorted_votes(poll: Poll, votes: List[Vote]) -> InstrumentedList:
    """Sort the votes depending on the poll's current settings."""

    def get_user_name(vote):
        """Get the name of user to sort votes."""
        return vote.user.name

    if poll.user_sorting == UserSorting.name.name:
        votes.sort(key=get_user_name)

    return votes


def get_sorted_doodle_votes(poll: Poll, votes: List[Vote]) -> Dict[str, List[Vote]]:
    """Sort the votes depending on the poll's current settings."""
    doodle_answers = ["yes", "maybe", "no"]

    votes_by_answer = {}
    for key in doodle_answers:
        # First get all votes that match the key
        votes_for_answer = []
        for vote in votes:
            if vote.type == key:
                votes_for_answer.append(vote)

        # If there are no answers, just continue
        if len(votes_for_answer) == 0:
            continue

        votes_by_answer[key] = votes_for_answer

    return votes_by_answer
