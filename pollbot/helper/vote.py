"""Helper functions for votes."""
from pollbot.helper.enums import UserSorting


def get_sorted_votes(poll, votes):
    """Sort the votes depending on the poll's current settings."""

    def get_user_name(vote):
        """Get the name of user to sort votes."""
        return vote.user.name

    if poll.user_sorting == UserSorting.name.name:
        votes.sort(key=get_user_name)

    return votes


def get_sorted_doodle_votes(poll, votes):
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
