from telegram.error import BadRequest, Unauthorized

from pollbot.models import Reference
from pollbot.i18n import i18n
from pollbot.helper.enums import PollType


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
        except Unauthorized as e:
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


def poll_required(function):
    """Return if the poll does not exist in the context object."""

    def wrapper(session, context):
        if context.poll is None:
            return i18n.t("callback.poll_no_longer_exists", locale=context.user.locale)

        return function(session, context, context.poll)

    return wrapper


def poll_allows_multiple_votes(poll):
    """Check whether the poll allows multiple votes."""
    multiple_poll_types = [
        PollType.block_vote.name,
        PollType.limited_vote.name,
        PollType.cumulative_vote.name,
    ]

    return poll.poll_type in multiple_poll_types
