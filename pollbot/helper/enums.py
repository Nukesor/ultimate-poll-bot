"""Helper enums to properly map several properties of Polls and alike."""
from enum import Enum, unique


@unique
class PollCreationStep(Enum):
    """Helper class to map the creation steps of a Poll."""

    name = 1
    description = 2
    options = 3
    done = 4


@unique
class PollType(Enum):
    """Helper class to specify the different types of Polls."""

    single_vote = 1
    multiple_votes = 2


poll_type_translation = {}
for poll_type in PollType:
    name = poll_type.name.capitalize()
    name.replace('_', ' ')
    poll_type_translation[poll_type.name] = name


@unique
class VoteType(Enum):
    """Helper enum to specify the different types of possible votes."""

    yes = 1
    no = 2
    maybe = 3


@unique
class CallbackType(Enum):
    """A class representing callback types."""

    # Poll creation
    show_poll_type_keyboard = 0
    change_poll_type = 1
    toggle_anonymity = 2
    skip_description = 3
    all_options_entered = 4
    cancel = 8


@unique
class CallbackResult(Enum):
    """A class representing callback results."""

    empty = 0
    true = 1
    false = 2
