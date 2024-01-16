import string

from sqlalchemy.orm.collections import InstrumentedList

from pollbot.models.option import Option


def get_option_indices(options: list[Option] | InstrumentedList) -> list[str]:
    """Simple helper to dynamically create indices/letters for option displaying."""
    indices = list(string.ascii_lowercase)
    if len(options) > len(indices):
        difference = len(options) - len(indices) + 1
        for i in range(1, difference):
            indices.append(str(i))

    return indices
