"""Callback functions needed during creation of a Poll."""
from pollbot.helper.enums import VoteType, VoteResultType
from pollbot.helper.display import update_poll_messages

from pollbot.models import PollOption, Vote


def handle_vote(session, context):
    """Handle any clicks on vote buttons."""
    option = session.query(PollOption).get(context.payload)
    poll = option.poll
    user = context.user

    # Single votes
    if poll.vote_type == VoteType.single_vote.name:
        existing_vote = session.query(Vote) \
            .filter(Vote.poll == poll) \
            .filter(Vote.user == user) \
            .one_or_none()
        # Changed vote
        if existing_vote and existing_vote.poll_option != option:
            existing_vote.poll_option = option
        # Voted for the same thing again
        elif existing_vote and existing_vote.poll_option == option:
            session.delete(existing_vote)
        # First vote on this poll
        elif existing_vote is None:
            vote = Vote(VoteResultType.yes.name, user, option)
            session.add(vote)

    # Multi votes
    elif poll.vote_type == VoteType.multiple_votes.name:
        existing_vote = session.query(Vote) \
            .filter(Vote.poll_option == option) \
            .filter(Vote.user == user) \
            .one_or_none()
        # Remove vote
        if existing_vote:
            session.delete(existing_vote)
        # Add vote to option
        elif existing_vote is None:
            vote = Vote(VoteResultType.yes.name, user, option)
            session.add(vote)

    context.query.answer('Vote registered')
    session.commit()
    update_poll_messages(session, context.bot, poll)
