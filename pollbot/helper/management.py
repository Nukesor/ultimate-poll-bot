"""Poll creation helper."""
import math
from sqlalchemy import func

from pollbot.models import (
    User,
    PollOption,
    Vote,
)
from pollbot.helper.display import get_poll_text


def get_poll_management_text(session, poll):
    """Create the management interface for a poll."""
    poll_text = get_poll_text(session, poll)

    management_text = 'Manage your poll:\n\n'
    management_text += poll_text

    return management_text
