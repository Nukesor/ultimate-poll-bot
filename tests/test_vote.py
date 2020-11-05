from pollbot.models import Option, Poll, Vote
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exists


class TestVote:
    def test_unique_ordering(self, session, user, poll):
        """
        Test if a session is unique.

        Args:
            self: (todo): write your description
            session: (todo): write your description
            user: (todo): write your description
            poll: (todo): write your description
        """
        option = Option(poll, "option 0")
        session.add(option)
        vote = Vote(user, option)
        vote.priority = 0
        session.add(vote)
        with pytest.raises(IntegrityError):
            vote_same_index = Vote(user, option)
            vote_same_index.priority = 0
            session.add(vote_same_index)
            session.commit()

    def test_cascades_dont_delete_poll(self, session, user, poll):
        """
        Deletes a poll.

        Args:
            self: (todo): write your description
            session: (todo): write your description
            user: (todo): write your description
            poll: (todo): write your description
        """
        option = Option(poll, "option 0")
        session.add(option)
        vote = Vote(user, option)
        vote.priority = 0
        session.add(vote)
        session.commit()
        session.delete(vote)
        session.commit()
        poll_exists = session.query(exists().where(Poll.id == poll.id)).scalar()
        assert poll_exists

    def test_cascades_delete_vote(self, session, user, poll):
        """
        Deletes the vote for a poll.

        Args:
            self: (todo): write your description
            session: (todo): write your description
            user: (todo): write your description
            poll: (todo): write your description
        """
        option = Option(poll, "option 0")
        session.add(option)
        vote = Vote(user, option)
        vote.priority = 0
        session.add(vote)
        session.commit()
        session.delete(poll)
        session.commit()
        assert session.query(Vote).count() == 0
