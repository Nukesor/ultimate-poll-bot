"""The poll management text."""
from .poll import get_poll_text


def get_poll_management_text(session, poll, show_warning=False):
    """Create the management interface for a poll."""
    poll_text = get_poll_text(session, poll, show_warning, management=True)

    return poll_text
