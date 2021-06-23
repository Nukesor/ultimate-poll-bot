"""Callback functions needed during creation of a Poll."""
from typing import Optional

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm.exc import NoResultFound, ObjectDeletedError, StaleDataError
from sqlalchemy.orm.scoping import scoped_session

from pollbot.enums import CallbackResult, PollType
from pollbot.helper.stats import increase_stat
from pollbot.i18n import i18n
from pollbot.models import Vote
from pollbot.models.option import Option
from pollbot.models.poll import Poll
from pollbot.poll.helper import poll_allows_cumulative_votes
from pollbot.poll.update import update_poll_messages
from pollbot.telegram.callback_handler.context import CallbackContext


def handle_vote(
    session: scoped_session, context: CallbackContext, option: Option
) -> None:
    """Handle any clicks on vote buttons."""
    # Remove the poll, in case it got deleted, but we didn't manage to kill all references
    if option is None:
        if context.query.message is not None:
            context.query.message.edit_text(
                i18n.t("deleted.polls", locale=context.user.locale)
            )
        else:
            context.bot.edit_message_text(
                i18n.t("deleted.polls", locale=context.user.locale),
                inline_message_id=context.query.inline_message_id,
            )
        return

    poll = option.poll
    update_poll = False
    try:
        # Single vote
        if poll.poll_type == PollType.single_vote.name:
            update_poll = handle_single_vote(session, context, option)
        # Block vote
        elif poll.poll_type == PollType.block_vote.name:
            update_poll = handle_block_vote(session, context, option)
        # Limited vote
        elif poll.poll_type == PollType.limited_vote.name:
            update_poll = handle_limited_vote(session, context, option)
        # Cumulative vote
        elif poll.poll_type == PollType.cumulative_vote.name:
            update_poll = handle_cumulative_vote(session, context, option)
        elif poll.poll_type == PollType.count_vote.name:
            update_poll = handle_cumulative_vote(
                session, context, option, limited=False
            )
        elif poll.poll_type == PollType.doodle.name:
            update_poll = handle_doodle_vote(session, context, option)
        elif poll.poll_type == PollType.priority.name:
            update_poll = handle_priority_vote(session, context, option)
        else:
            raise Exception("Unknown poll type")
        session.commit()

    except IntegrityError:
        # Double vote. Rollback the transaction and ignore the second vote
        session.rollback()
        return
    except ObjectDeletedError:
        # Vote on already removed vote. Rollback the transaction and ignore
        session.rollback()
        return
    except StaleDataError:
        # Try to edit a vote that has already been deleted.
        # This happens, if users spam the vote buttons.
        # Rollback the transaction and ignore
        session.rollback()
        return
    except OperationalError:
        # This happens, when a deadlock is created.
        # That can be caused by users spamming the vote button.
        session.rollback()
        return
    except NoResultFound:
        # This can happen if a user concurrently upvotes and downvotes an option.
        # -> Downvote deletes the Vote, upvote tries to change the Vote.
        session.rollback()
        return

    # Update the reference depending on message type
    message = context.query.message
    inline_message_id = context.query.inline_message_id
    if update_poll:
        if message is not None:
            update_poll_messages(
                session, context.bot, poll, message.message_id, context.user
            )
        else:
            update_poll_messages(
                session, context.bot, poll, inline_message_id=inline_message_id
            )

    increase_stat(session, "votes")
    session.commit()


def respond_to_vote(
    session: scoped_session,
    line: str,
    context: CallbackContext,
    poll: Poll,
    remaining_votes: Optional[int] = None,
    limited: bool = False,
) -> None:
    """Get the formatted response for a user."""
    locale = poll.locale
    votes = (
        session.query(Vote)
        .filter(Vote.user == context.user)
        .filter(Vote.poll == poll)
        .all()
    )

    if limited:
        line += i18n.t("callback.vote.votes_left", locale=locale, count=remaining_votes)

    lines = [line]
    lines.append(i18n.t("callback.vote.your_votes", locale=locale))
    for vote in votes:
        if poll_allows_cumulative_votes(poll):
            lines.append(f" {vote.option.name} ({vote.vote_count}), ")
        else:
            lines.append(f" {vote.option.name}")

    message = "".join(lines)

    # Inline query responses cannot be longer than 200 characters
    # Restrict it, since we get an MessageTooLong error otherwise
    if len(message) > 190:
        message = message[0:190]

    context.query.answer(message)


def handle_single_vote(
    session: scoped_session, context: CallbackContext, option: Option
) -> bool:
    """Handle a single vote."""
    locale = option.poll.locale
    existing_vote = (
        session.query(Vote)
        .filter(Vote.poll == option.poll)
        .filter(Vote.user == context.user)
        .one_or_none()
    )

    # Changed vote
    if existing_vote and existing_vote.option != option:
        existing_vote.option = option
        vote_changed = i18n.t("callback.vote.changed", locale=locale)
        respond_to_vote(session, vote_changed, context, option.poll)

    # Voted for the same thing again
    elif existing_vote and existing_vote.option == option:
        session.delete(existing_vote)
        vote_removed = i18n.t("callback.vote.removed", locale=locale)
        context.query.answer(vote_removed)

    # First vote on this poll
    elif existing_vote is None:
        vote = Vote(context.user, option)
        session.add(vote)
        vote_registered = i18n.t("callback.vote.registered", locale=locale)
        respond_to_vote(session, vote_registered, context, option.poll)

    return True


def handle_block_vote(
    session: scoped_session, context: CallbackContext, option: Option
) -> bool:
    """Handle a block vote."""
    locale = option.poll.locale
    existing_vote = (
        session.query(Vote)
        .filter(Vote.option == option)
        .filter(Vote.user == context.user)
        .one_or_none()
    )

    # Remove vote
    if existing_vote:
        session.delete(existing_vote)
        vote_removed = i18n.t("callback.vote.removed", locale=locale)
        respond_to_vote(session, vote_removed, context, option.poll)

    # Add vote
    elif existing_vote is None:
        vote = Vote(context.user, option)
        session.add(vote)
        vote_registered = i18n.t("callback.vote.registered", locale=locale)
        respond_to_vote(session, vote_registered, context, option.poll)

    return True


def handle_limited_vote(
    session: scoped_session, context: CallbackContext, option: Option
) -> bool:
    """Handle a limited vote."""
    locale = option.poll.locale
    existing_vote = (
        session.query(Vote)
        .filter(Vote.option == option)
        .filter(Vote.user == context.user)
        .one_or_none()
    )

    vote_count = (
        session.query(Vote)
        .filter(Vote.poll == option.poll)
        .filter(Vote.user == context.user)
        .count()
    )
    allowed_votes = option.poll.number_of_votes

    # Remove vote
    if existing_vote:
        session.delete(existing_vote)

        vote_removed = i18n.t("callback.vote.removed", locale=locale)
        remaining_votes = allowed_votes - (vote_count - 1)
        respond_to_vote(
            session, vote_removed, context, option.poll, remaining_votes, True
        )

    # Add vote
    elif existing_vote is None and vote_count < allowed_votes:
        vote = Vote(context.user, option)
        session.add(vote)
        vote_registered = i18n.t("callback.vote.registered", locale=locale)
        remaining_votes = allowed_votes - (vote_count + 1)
        respond_to_vote(
            session, vote_registered, context, option.poll, remaining_votes, True
        )

    # Max votes reached
    else:
        no_left = i18n.t("callback.vote.no_left", locale=locale)
        respond_to_vote(session, no_left, context, option.poll)
        return False

    return True


def handle_cumulative_vote(
    session: scoped_session,
    context: CallbackContext,
    option: Option,
    limited: bool = True,
) -> bool:
    """Handle a cumulative vote."""
    locale = option.poll.locale
    existing_vote = (
        session.query(Vote)
        .filter(Vote.option == option)
        .filter(Vote.user == context.user)
        .one_or_none()
    )

    vote_count = (
        session.query(func.sum(Vote.vote_count))
        .filter(Vote.poll == option.poll)
        .filter(Vote.user == context.user)
        .one()
    )
    vote_count = vote_count[0]
    if vote_count is None:
        vote_count = 0

    action = context.callback_result
    allowed_votes = 10000000
    if limited:
        allowed_votes = option.poll.number_of_votes

    # Upvote, but no votes left
    if limited and action == CallbackResult.yes and vote_count >= allowed_votes:
        no_left = i18n.t("callback.vote.no_left", locale=locale)
        respond_to_vote(session, no_left, context, option.poll)
        return False

    # Early return if downvote on non existing vote
    if existing_vote is None and action == CallbackResult.no:
        respond_to_vote(session, "Cannot downvote this option.", context, option.poll)
        return False

    if existing_vote:
        # Add to an existing vote
        if action == CallbackResult.yes:
            existing_vote.vote_count += 1
            session.flush()
            remaining_votes = allowed_votes - (vote_count + 1)
            vote_registered = i18n.t("callback.vote.registered", locale=locale)
            respond_to_vote(
                session, vote_registered, context, option.poll, remaining_votes, limited
            )

        # Remove from existing vote
        elif action == CallbackResult.no:
            existing_vote.vote_count -= 1

            # Delete vote if necessary
            if existing_vote.vote_count <= 0:
                session.delete(existing_vote)

            session.flush()
            remaining_votes = allowed_votes - (vote_count - 1)
            vote_removed = i18n.t("callback.vote.removed", locale=locale)
            respond_to_vote(
                session, vote_removed, context, option.poll, remaining_votes, limited
            )

    # Add new vote
    elif existing_vote is None and action == CallbackResult.yes:
        vote = Vote(context.user, option)
        session.add(vote)
        session.flush()
        remaining_votes = allowed_votes - (vote_count + 1)
        vote_registered = i18n.t("callback.vote.registered", locale=locale)
        respond_to_vote(
            session, vote_registered, context, option.poll, remaining_votes, limited
        )

    return True


def handle_doodle_vote(
    session: scoped_session, context: CallbackContext, option: Option
) -> bool:
    """Handle a doodle vote."""
    locale = option.poll.locale
    vote = (
        session.query(Vote)
        .filter(Vote.option == option)
        .filter(Vote.user == context.user)
        .one_or_none()
    )

    if context.callback_result is None:
        raise Exception("Unknown callback result")

    # Remove vote
    if vote is not None:
        vote.type = context.callback_result.name
        changed = i18n.t(
            "callback.vote.doodle_changed", locale=locale, vote_type=vote.type
        )
        context.query.answer(changed)

    # Add vote
    else:
        vote = Vote(context.user, option)
        vote.type = context.callback_result.name
        session.add(vote)
        registered = i18n.t(
            "callback.vote.doodle_registered", locale=locale, vote_type=vote.type
        )
        context.query.answer(registered)

    return True


def handle_priority_vote(
    session: scoped_session, context: CallbackContext, option: Option
) -> bool:
    """Handle a priority vote"""
    vote = (
        session.query(Vote)
        .filter(Vote.option == option)
        .filter(Vote.user == context.user)
        .one()
    )

    previous_priority = vote.priority
    # allow next vote to take this vote's place
    vote.priority = -1

    if context.callback_result is None:
        raise Exception("Unknown callback result")

    if context.callback_result.name == CallbackResult.increase_priority.name:
        direction = -1
    else:
        direction = 1

    next_vote = (
        session.query(Vote)
        .filter(Vote.user == context.user)
        .filter(Vote.poll == vote.poll)
        .filter(Vote.priority == previous_priority + direction)
        .one_or_none()
    )

    if next_vote is None:
        session.rollback()
        return False

    next_vote.priority -= direction
    session.flush()
    vote.priority = previous_priority + direction

    registered = i18n.t("callback.vote.registered", locale=option.poll.locale)
    context.query.answer(registered)

    return True
