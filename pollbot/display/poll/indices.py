import string


def get_option_indices(options):
    """Simple helper to dynamically create indices/letters for option displaying."""
    indices = list(string.ascii_lowercase)
    if len(options) > len(indices):
        difference = len(options) - len(indices) + 1
        for i in range(1, difference):
            indices.append(str(i))

    return indices
