"""Callback functions needed during creation of a Poll."""
from sqlalchemy import func

from pollbot.helper.enums import VoteType, VoteResultType, CallbackResult
from pollbot.helper.update import update_poll_messages

from pollbot.models import PollOption, Vote


def handle_vote(session, context):
    """Handle any clicks on vote buttons."""
    option = session.query(PollOption).get(context.payload)
    poll = option.poll

    # Single vote
    if poll.vote_type == VoteType.single_vote.name:
        handle_single_vote(session, context, option)
    # Block vote
    elif poll.vote_type == VoteType.block_vote.name:
        handle_block_vote(session, context, option)
    # Limited vote
    elif poll.vote_type == VoteType.limited_vote.name:
        handle_limited_vote(session, context, option)
    # Cumulative vote
    elif poll.vote_type == VoteType.cumulative_vote.name:
        handle_cumulative_vote(session, context, option)

    session.commit()
    update_poll_messages(session, context.bot, poll)


def handle_single_vote(session, context, option):
    """Handle a single vote."""
    existing_vote = session.query(Vote) \
        .filter(Vote.poll == option.poll) \
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


def handle_block_vote(session, context, option):
    """Handle a block vote."""
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


def handle_limited_vote(session, context, option):
    """Handle a limited vote."""
    existing_vote = session.query(Vote) \
        .filter(Vote.poll_option == option) \
        .filter(Vote.user == context.user) \
        .one_or_none()

    vote_count = session.query(Vote) \
        .filter(Vote.poll == option.poll) \
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


def handle_cumulative_vote(session, context, option):
    """Handle a cumulative vote."""
    existing_vote = session.query(Vote) \
        .filter(Vote.poll_option == option) \
        .filter(Vote.user == context.user) \
        .one_or_none()

    vote_count = session.query(func.sum(Vote.vote_count)) \
        .filter(Vote.poll == option.poll) \
        .filter(Vote.user == context.user) \
        .count()

    action = context.callback_result
    if action == CallbackResult.vote_yes and vote_count >= option.poll.number_of_votes:
        context.query.answer('You have no votes left.')

    if existing_vote is None and action == CallbackResult.vote_no:
        context.query.answer('You cannot downvote this option.')

    # Remove vote
    if existing_vote:
        if action == CallbackResult.vote_yes:
            existing_vote.vote_count += 1
            context.query.answer('Vote added')
        elif action == CallbackResult.vote_no:
            existing_vote.vote_count -= 1
            context.query.answer('Vote removed')

        if existing_vote.vote_count <= 0:
            session.delete(existing_vote)

    # Add vote to option
    elif existing_vote is None and action == CallbackResult.vote_yes:
        vote = Vote(VoteResultType.yes.name, context.user, option)
        vote.vote_count += 1
        session.add(vote)
        context.query.answer('Vote registered')
