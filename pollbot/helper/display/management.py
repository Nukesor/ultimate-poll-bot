"""The poll management text."""
from .poll import get_poll_text


def get_poll_management_text(session, poll, show_warning=False):
    """Create the management interface for a poll."""
    poll_text = get_poll_text(session, poll, show_warning)

    # Poll is closed, the options are not important any longer
    if poll.closed:
        return poll_text

    management_text = 'Manage your poll:\n\n'
    management_text += poll_text

    return management_text
