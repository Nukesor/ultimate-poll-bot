"""Callback functions needed during creation of a Poll."""
from sqlalchemy import func

from pollbot.helper import poll_is_cumulative
from pollbot.helper.enums import VoteType, VoteResultType, CallbackResult
from pollbot.helper.update import update_poll_messages

from pollbot.models import PollOption, Vote


def handle_vote(session, context):
    """Handle any clicks on vote buttons."""
    # Remove the poll, in case it got deleted, but we didn't manage to kill all references
    option = session.query(PollOption).get(context.payload)
    if option is None:
        if context.query.message is not None:
            context.query.message.edit_text('This poll has been permanently deleted.')
        else:
            context.bot.edit_message_text(
                'This poll has been permanently deleted.',
                inline_message_id=context.query.inline_message_id,
            )

    poll = option.poll

    # Single vote
    if poll.vote_type == VoteType.single_vote.name:
        update_poll = handle_single_vote(session, context, option)
    # Block vote
    elif poll.vote_type == VoteType.block_vote.name:
        update_poll = handle_block_vote(session, context, option)
    # Limited vote
    elif poll.vote_type == VoteType.limited_vote.name:
        update_poll = handle_limited_vote(session, context, option)
    # Cumulative vote
    elif poll.vote_type == VoteType.cumulative_vote.name:
        update_poll = handle_cumulative_vote(session, context, option)

    session.commit()
    if update_poll:
        update_poll_messages(session, context.bot, poll)


def respond_to_vote(session, line, context, poll):
    """Get the formatted response for a user."""
    votes = session.query(Vote) \
        .filter(Vote.user == context.user) \
        .filter(Vote.poll == poll) \
        .all()

    lines = [line]
    lines.append('Your votes so far:')
    for vote in votes:
        if poll_is_cumulative(poll):
            lines.append(f'{vote.option.name} ({vote.vote_count}), ')
        else:
            lines.append(vote.poll_option.name)

    message = '\n'.join(lines)

    context.query.answer(message)


def handle_single_vote(session, context, option):
    """Handle a single vote."""
    existing_vote = session.query(Vote) \
        .filter(Vote.poll == option.poll) \
        .filter(Vote.user == context.user) \
        .one_or_none()
    # Changed vote
    if existing_vote and existing_vote.poll_option != option:
        existing_vote.poll_option = option
        respond_to_vote(session, 'Vote changed1', context, option.poll)

    # Voted for the same thing again
    elif existing_vote and existing_vote.poll_option == option:
        session.delete(existing_vote)
        context.query.answer('Vote removed!')

    # First vote on this poll
    elif existing_vote is None:
        vote = Vote(VoteResultType.yes.name, context.user, option)
        session.add(vote)
        respond_to_vote(session, 'Vote registered!', context, option.poll)

    return True


def handle_block_vote(session, context, option):
    """Handle a block vote."""
    existing_vote = session.query(Vote) \
        .filter(Vote.poll_option == option) \
        .filter(Vote.user == context.user) \
        .one_or_none()

    # Remove vote
    if existing_vote:
        session.delete(existing_vote)
        respond_to_vote(session, 'Vote removed!', context, option.poll)

    # Add vote
    elif existing_vote is None:
        vote = Vote(VoteResultType.yes.name, context.user, option)
        session.add(vote)
        respond_to_vote(session, 'Vote registered!', context, option.poll)

    return True


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
        respond_to_vote(session, 'Vote removed!', context, option.poll)

    # Add vote
    elif existing_vote is None and vote_count < option.poll.number_of_votes:
        vote = Vote(VoteResultType.yes.name, context.user, option)
        session.add(vote)
        respond_to_vote(session, 'Vote registered!', context, option.poll)

    # Max votes reached
    else:
        respond_to_vote(session, 'No votes left!', context, option.poll)
        return False

    return True


def handle_cumulative_vote(session, context, option):
    """Handle a cumulative vote."""
    existing_vote = session.query(Vote) \
        .filter(Vote.poll_option == option) \
        .filter(Vote.user == context.user) \
        .one_or_none()

    vote_count = session.query(func.sum(Vote.vote_count)) \
        .filter(Vote.poll == option.poll) \
        .filter(Vote.user == context.user) \
        .one()
    vote_count = vote_count[0]
    if vote_count is None:
        vote_count = 0

    action = context.callback_result
    allowed_votes = option.poll.number_of_votes

    # Upvote, but no votes left
    if action == CallbackResult.vote_yes and vote_count >= allowed_votes:
        respond_to_vote(session, 'No votes left!', context, option.poll)
        return False

    # Early return if downvote on non existing vote
    if existing_vote is None and action == CallbackResult.vote_no:
        respond_to_vote(session, 'Cannot downvote this option.', context, option.poll)
        return False

    if existing_vote:
        # Add to an existing vote
        if action == CallbackResult.vote_yes:
            existing_vote.vote_count += 1
            session.commit()
            total_vote_count = allowed_votes - (vote_count + 1)
            respond_to_vote(session, f'Vote added ({total_vote_count} left)!', context, option.poll)

        # Remove from existing vote
        elif action == CallbackResult.vote_no:
            existing_vote.vote_count -= 1
            session.commit()
            total_vote_count = allowed_votes - (vote_count - 1)
            respond_to_vote(session, f'Vote removed ({total_vote_count} left)!', context, option.poll)

        # Delete vote if necessary
        if existing_vote.vote_count <= 0:
            session.delete(existing_vote)
            session.commit()

    # Add new vote
    elif existing_vote is None and action == CallbackResult.vote_yes:
        vote = Vote(VoteResultType.yes.name, context.user, option)
        session.add(vote)
        session.commit()
        respond_to_vote(session, f'Vote registered ({total_vote_count} left)!', context, option.poll)

    return True
