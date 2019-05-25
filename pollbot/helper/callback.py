"""Helper for callback queries.

This file is for mapping human readable strings to integers
"""
from enum import Enum, unique


@unique
class CallbackType(Enum):
    """A class representing callback types."""

    cancel = 11


@unique
class CallbackResult(Enum):
    """A class representing callback results."""

    true = 1
    false = 2
