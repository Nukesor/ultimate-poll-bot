from sqlalchemy.orm import Session
from telegram import Poll as NativePoll

from pollbot.enums import PollType
from pollbot.models import Poll
from pollbot.poll.option import add_multiple_options


def merge_from_native_poll(
    poll: Poll, native_poll: NativePoll, session: Session
) -> None:
    """Fills information in a pollbot `Poll` with data extracted from a native Telegram poll"""
    poll.created_from_native = True
    poll.poll_type = convert_poll_type(native_poll).name
    poll.name = native_poll.question
    poll.anonymous = native_poll.is_anonymous

    # Get all options, strip them and add them
    options = [o.text for o in native_poll.options]
    options_to_add = list(map(str.strip, options))
    add_multiple_options(session, poll, options_to_add)


def convert_poll_type(native_poll: NativePoll) -> PollType:
    if native_poll.allows_multiple_answers:
        return PollType.block_vote
    else:
        return PollType.single_vote
