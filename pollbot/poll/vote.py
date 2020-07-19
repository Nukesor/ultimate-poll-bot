"""Helper functions for votes."""
import random
from typing import List

from pollbot.enums import UserSorting
from pollbot.models import Poll, User, Vote, Option


def init_votes(session, poll: Poll, user: User):
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


def init_votes_for_new_options(session, poll: Poll, added_options: List[str]):
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

    existing_options_count = len(poll.options) - len(new_options)

    users_that_voted = (
        session.query(User).join(User.votes).filter(Vote.poll == poll).all()
    )

    for user in users_that_voted:
        for index, option in enumerate(new_options):
            print(f"New vote with priority {existing_options_count + index}")
            vote = Vote(user, option)
            vote.priority = existing_options_count + index
            user.votes.append(vote)


def get_sorted_votes(poll: Poll, votes: List[Vote]):
    """Sort the votes depending on the poll's current settings."""

    def get_user_name(vote):
        """Get the name of user to sort votes."""
        return vote.user.name

    if poll.user_sorting == UserSorting.name.name:
        votes.sort(key=get_user_name)

    return votes


def get_sorted_doodle_votes(poll: Poll, votes: List[Vote]):
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
