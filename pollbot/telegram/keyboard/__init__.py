"""Reply keyboards."""


def get_start_button_payload(poll, action):
    """Compile the /start action payload for a certain action."""
    # Compress the uuid a little and remove the 4 hypens
    uuid = str(poll.uuid).replace('-', '')

    return f'{uuid}-{action.value}'


from .creation import * # noqa
from .management import * # noqa
from .settings import * # noqa
from .vote import * # noqa
from .external import * # noqa
from .user import * # noqa
from .misc import * # noqa
from .date_picker import * # noqa
