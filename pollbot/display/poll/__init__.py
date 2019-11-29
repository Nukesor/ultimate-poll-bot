"""Get the text describing the current state of the poll."""
from pollbot.helper import (
    poll_has_limited_votes,
)
from pollbot.models import (
    User,
    PollOption,
    Vote,
)


class Context():
    """Context for poll text creatio.

    This class contains all necessary information and flags, that
    are needed to decide in which way a poll should be displayed.
    """

    def __init__(self, session, poll):
        """Contructor."""
        self.total_user_count = session.query(User.id) \
            .join(Vote) \
            .join(PollOption) \
            .filter(PollOption.poll == poll) \
            .group_by(User.id) \
            .count()

        # Flags
        self.anonymous = poll.anonymous
        self.show_results = poll.should_show_result()
        self.show_percentage = poll.show_percentage
        self.limited_votes = poll_has_limited_votes(poll)
