"""Callback functions needed during creation of a Poll."""
from pollbot.helper.enums import PollType, VoteType
from pollbot.helper.management import get_poll_management_text
from pollbot.helper.keyboard import get_vote_keyboard

from pollbot.models import PollOption, Vote


def handle_vote(session, bot, context):
    """Change the initial keyboard to poll type keyboard."""
    option = session.query(PollOption).get(context.payload)
    poll = option.poll
    user = context.user

    # Single votes
    if poll.type == PollType.single_vote.name:
        existing_vote = session.query(Vote) \
            .filter(Vote.poll == poll) \
            .filter(Vote.user == user) \
            .one_or_none()
        # Changed vote
        if existing_vote and existing_vote.poll_option != option:
            existing_vote.poll_option = option
        # Voted for the same thing again
        elif existing_vote and existing_vote.poll_option == option:
            return
        # First vote on this poll
        elif existing_vote is None:
            vote = Vote(VoteType.yes.name, user, option)
            session.add(vote)

    # Multi votes
    elif poll.type == PollType.multiple_votes.name:
        existing_vote = session.query(Vote) \
            .filter(Vote.poll_option == option) \
            .filter(Vote.user == user) \
            .one_or_none()
        # Remove vote
        if existing_vote:
            session.delete(existing_vote)
        # Add vote to option
        elif existing_vote is None:
            vote = Vote(VoteType.yes.name, user, option)
            session.add(vote)

    session.commit()

    text = get_poll_management_text(session, poll)
    keyboard = get_vote_keyboard(poll)
    context.query.message.edit_text(text, reply_markup=keyboard, parse_mode='markdown')
