from pollbot.helper.enums import (
    UserSorting,
    PollType,
)


def get_sorted_votes(poll, votes):
    """Sort the votes depending on the poll's current settings."""
    def get_user_name(vote):
        """Get the name of user to sort votes."""
        return vote.user.name

    def get_doodle_int(vote):
        """Get the sorting key for the vote type."""
        mapping = {
            'yes': 1,
            'maybe': 2,
            'no': 3,
        }
        return mapping[vote.type]

    if poll.poll_type == PollType.doodle.name:
        votes.sort(key=get_doodle_int)

    elif poll.user_sorting == UserSorting.user_name.name:
        votes.sort(key=get_user_name)

    return votes
