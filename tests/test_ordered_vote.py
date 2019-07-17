from pollbot.models import OrderedVote, PollOption, Poll, Vote
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exists

class TestOrderedVote:
    def test_unique_ordering(self, session, user, poll):
        option = PollOption(poll, 'option 0')
        session.add(option)
        vote = OrderedVote(user, option, 0)
        session.add(vote)
        with pytest.raises(IntegrityError):
            vote_same_index = OrderedVote(user, option, 0)
            session.add(vote_same_index)
            session.commit()

    def test_cascades_dont_delete_poll(self, session, user, poll):
        option = PollOption(poll, 'option 0')
        session.add(option)
        vote = OrderedVote(user, option, 0)
        session.add(vote)
        session.commit()
        session.delete(vote)
        session.commit()
        poll_exists = session.query(exists().where(Poll.id == poll.id)).scalar()
        assert poll_exists

    def test_cascades_delete_vote(self, session, user, poll):
        option = PollOption(poll, 'option 0')
        session.add(option)
        vote = OrderedVote(user, option, 0)
        session.add(vote)
        session.commit()
        session.delete(poll)
        session.commit()
        assert session.query(Vote).count() == 0
