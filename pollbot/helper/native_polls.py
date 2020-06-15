from sqlalchemy.orm import Session
from telegram import Poll as NativePoll

from pollbot.helper.creation import add_text_options_from_list
from pollbot.helper.enums import PollType
from pollbot.models import Poll


def merge_from_native_poll(
    poll: Poll, native_poll: NativePoll, session: Session
) -> None:
    """Fills information in a pollbot `Poll` with data extracted from a native Telegram poll"""
    poll.created_from_native = True
    poll.poll_type = convert_poll_type(native_poll).name
    poll.name = native_poll.question
    poll.anonymous = native_poll.is_anonymous
    add_text_options_from_list(session, poll, [o.text for o in native_poll.options])


def convert_poll_type(native_poll: NativePoll) -> PollType:
    if native_poll.allows_multiple_answers:
        return PollType.block_vote
    else:
        return PollType.single_vote
