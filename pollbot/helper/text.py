

def split_text(lines):
    """Split a text devided by newline into chunks of about 4000 characters."""
    chunks = []
    current_chunk = []

    chars = 0
    for line in lines:
        chars += len(line)
        if chars < 4000:
            current_chunk.append(line)
        else:
            chunks.append(current_chunk)
            current_chunk = [line]
            chars = len(line)

    chunks.append(current_chunk)

    return chunks
