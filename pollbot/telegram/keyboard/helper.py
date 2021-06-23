from pollbot.enums import StartAction
from pollbot.models.poll import Poll


def get_start_button_payload(poll: Poll, action: StartAction) -> str:
    """Compile the /start action payload for a certain action."""
    # Compress the uuid a little and remove the 4 hypens
    uuid = str(poll.uuid).replace("-", "")

    return f"{uuid}-{action.value}"
