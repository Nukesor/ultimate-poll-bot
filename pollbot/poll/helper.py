import random

from pollbot.enums import PollType
from pollbot.i18n import i18n
from pollbot.models import Poll, User, Vote, Option, Reference
from telegram.error import BadRequest, Unauthorized


def init_votes(session, poll, user):
    """
    Since Priority votes always need priorities, call this to create a vote
    for every option in the poll with a random priority for the given user
    """
    assert poll.is_priority()

    votes_exist = (
        session.query(Vote).filter(Vote.user == user).filter(Vote.poll == self).first()
        is not None
    )

    if votes_exist:
        return

    votes = []
    for index, option in enumerate(random.sample(self.options, len(self.options))):
        vote = Vote(user, option)
        vote.priority = index
        votes.append(vote)
    session.add_all(votes)


def init_votes_for_new_options(session, poll):
    """
    When a new option is added, we need to create new votes
    for all users that have already voted for this poll
    """
    if not poll.is_priority():
        return

    users = session.query(User).join(User.votes).filter(Vote.poll == poll).all()

    new_options = (
        session.query(Option)
        .filter(Option.poll == poll)
        .outerjoin(Vote)
        .filter(Vote.id.is_(None))
        .all()
    )

    existing_options_count = len(poll.options) - len(poll_options)

    for user in users:
        for index, option in enumerate(new_options):
            vote = Vote(user, option)
            vote.priority = existing_options_count + index
            user.votes.append(vote)


def clone_poll(session, original_poll):
    """Create a clone from the current poll."""
    new_poll = Poll(original_poll.user)
    new_poll.created = True
    session.add(new_poll)

    new_poll.name = original_poll.name
    new_poll.description = original_poll.description
    new_poll.poll_type = original_poll.poll_type
    new_poll.anonymous = original_poll.anonymous
    new_poll.number_of_votes = original_poll.number_of_votes
    new_poll.allow_new_options = original_poll.allow_new_options
    new_poll.option_sorting = original_poll.option_sorting
    new_poll.user_sorting = original_poll.user_sorting
    new_poll.results_visible = original_poll.results_visible
    new_poll.show_percentage = original_poll.show_percentage

    for option in original_poll.options:
        new_option = Option(new_poll, option.name)
        new_option.description = option.description
        new_option.is_date = option.is_date
        new_option.index = option.index
        session.add(new_option)

    return new_poll


def remove_old_references(session, bot, poll, user):
    """Remove old references in private chats."""
    references = (
        session.query(Reference)
        .filter(Reference.poll == poll)
        .filter(Reference.user == user)
        .all()
    )

    for reference in references:
        try:
            bot.delete_message(
                chat_id=reference.user_id, message_id=reference.message_id
            )
        except Unauthorized:
            session.delete(reference)
        except BadRequest as e:
            if (
                e.message.startswith("Message_id_invalid")
                or e.message.startswith("Message can't be edited")
                or e.message.startswith("Message to edit not found")
                or e.message.startswith("Chat not found")
                or e.message.startswith("Can't access the chat")
            ):
                session.delete(reference)

        session.commit()


def calculate_total_votes(poll):
    """Calculate the total number of votes of a poll."""
    total = 0
    for vote in poll.votes:
        total += vote.vote_count

    return total


def translate_poll_type(poll_type, locale):
    """Translate a poll type to the users language."""
    mapping = {
        PollType.single_vote.name: i18n.t("poll_types.single_vote", locale=locale),
        PollType.doodle.name: i18n.t("poll_types.doodle", locale=locale),
        PollType.block_vote.name: i18n.t("poll_types.block_vote", locale=locale),
        PollType.limited_vote.name: i18n.t("poll_types.limited_vote", locale=locale),
        PollType.cumulative_vote.name: i18n.t(
            "poll_types.cumulative_vote", locale=locale
        ),
        PollType.count_vote.name: i18n.t("poll_types.count_vote", locale=locale),
        PollType.priority.name: i18n.t("poll_types.priority", locale=locale),
    }

    return mapping[poll_type]


def poll_allows_multiple_votes(poll):
    """Check whether the poll allows multiple votes."""
    multiple_poll_types = [
        PollType.block_vote.name,
        PollType.limited_vote.name,
        PollType.cumulative_vote.name,
    ]

    return poll.poll_type in multiple_poll_types


def poll_has_limited_votes(poll):
    """Check whether the poll has limited votes."""
    poll_type_with_vote_count = [
        PollType.limited_vote.name,
        PollType.cumulative_vote.name,
    ]

    return poll.poll_type in poll_type_with_vote_count


def poll_allows_cumulative_votes(poll):
    """Check whether this poll's type is cumulative."""
    return poll.poll_type in [PollType.cumulative_vote.name, PollType.count_vote.name]
