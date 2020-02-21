"""Some static stuff or helper functions."""
from telethon import types

from pollbot.i18n import i18n
from pollbot.config import config
from .enums import PollType


def translate_poll_type(poll_type, locale):
    """Translate a poll type to the users language."""
    mapping = {
        PollType.single_vote.name: i18n.t('poll_types.single_vote', locale=locale),
        PollType.doodle.name: i18n.t('poll_types.doodle', locale=locale),
        PollType.block_vote.name: i18n.t('poll_types.block_vote', locale=locale),
        PollType.limited_vote.name: i18n.t('poll_types.limited_vote', locale=locale),
        PollType.cumulative_vote.name: i18n.t('poll_types.cumulative_vote', locale=locale),
        PollType.count_vote.name: i18n.t('poll_types.count_vote', locale=locale),
        PollType.priority.name: i18n.t('poll_types.priority', locale=locale),
    }

    return mapping[poll_type]


def poll_required(function):
    """Return if the poll does not exist in the context object."""
    def wrapper(session, context):
        if context.poll is None:
            return i18n.t('callback.poll_no_longer_exists', locale=context.user.locale)

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


def poll_has_limited_votes(poll):
    """Check whether the poll has limited votes."""
    poll_type_with_vote_count = [
        PollType.limited_vote.name,
        PollType.cumulative_vote.name,
    ]

    return poll.poll_type in poll_type_with_vote_count


def poll_allows_cumulative_votes(poll):
    """Check whether this poll's type is cumulative."""
    return poll.poll_type in [
        PollType.cumulative_vote.name,
        PollType.count_vote.name
    ]


def calculate_total_votes(poll):
    """Calculate the total number of votes of a poll."""
    total = 0
    for vote in poll.votes:
        total += vote.vote_count

    return total


def get_escaped_bot_name():
    """Get the bot name escaped for markdown."""
    name = config['telegram']['bot_name']
    escaped = name.replace('_', '\_')

    return escaped


def get_peer_information(peer):
    """Get the id depending on the chat type."""
    if isinstance(peer, types.PeerUser):
        return peer.user_id, 'user'
    elif isinstance(peer, types.PeerChat):
        return peer.chat_id, 'peer'
    elif isinstance(peer, types.PeerChannel):
        return peer.channel_id, 'channel'
    else:
        raise Exception("Unknown chat type")
