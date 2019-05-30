"""Callback functions needed during creation of a Poll."""
from pollbot.helper.enums import VoteType, VoteResultType
from pollbot.helper.display import update_poll_messages

from pollbot.models import PollOption, Vote


def handle_vote(session, context):
    """Handle any clicks on vote buttons."""
    option = session.query(PollOption).get(context.payload)
    poll = option.poll

    # Single votes
    if poll.vote_type == VoteType.single_vote.name:
        handle_single_vote(session, context, option)
    # Multi votes
    elif poll.vote_type == VoteType.multiple_votes.name:
        handle_multi_vote(session, context, option)
    # Fix count vote
    elif poll.vote_type == VoteType.fix_votes.name:
        handle_fix_vote(session, context, option)

    session.commit()
    update_poll_messages(session, context.bot, poll)


def handle_single_vote(session, context, option):
    """Handle a single vote."""
    existing_vote = session.query(Vote) \
        .filter(Vote.poll == context.poll) \
        .filter(Vote.user == context.user) \
        .one_or_none()
    # Changed vote
    if existing_vote and existing_vote.poll_option != option:
        existing_vote.poll_option = option
        context.query.answer('Vote changed')
    # Voted for the same thing again
    elif existing_vote and existing_vote.poll_option == option:
        session.delete(existing_vote)
        context.query.answer('Vote removed')
    # First vote on this poll
    elif existing_vote is None:
        vote = Vote(VoteResultType.yes.name, context.user, option)
        session.add(vote)
        context.query.answer('Vote registered')


def handle_multi_vote(session, context, option):
    """Handle a Multi vote."""
    existing_vote = session.query(Vote) \
        .filter(Vote.poll_option == option) \
        .filter(Vote.user == context.user) \
        .one_or_none()
    # Remove vote
    if existing_vote:
        session.delete(existing_vote)
        context.query.answer('Vote removed')
        # Add vote to option
    elif existing_vote is None:
        vote = Vote(VoteResultType.yes.name, context.user, option)
        session.add(vote)
        context.query.answer('Vote registered')


def handle_fix_vote(session, context, option):
    """Handle a Fix count vote."""
    existing_vote = session.query(Vote) \
        .filter(Vote.poll_option == option) \
        .filter(Vote.user == context.user) \
        .one_or_none()

    vote_count = session.query(Vote) \
        .filter(Vote.poll == context.poll) \
        .filter(Vote.user == context.user) \
        .count()

    # Remove vote
    if existing_vote:
        session.delete(existing_vote)
        context.query.answer('Vote removed')

    # Add vote to option
    elif existing_vote is None and vote_count < option.poll.number_of_votes:
        vote = Vote(VoteResultType.yes.name, context.user, option)
        session.add(vote)
        context.query.answer('Vote registered')

    # Max votes reached
    else:
        context.query.answer('You have no votes left.')
