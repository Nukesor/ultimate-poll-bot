"""Helper for text handling."""
MAX_LENGTH = 4096


def split_text(lines, max_chunks=5):
    """Split the text into multiple chunks with a max of 4096 characters per chunk.

    Telegram's maximum message size is 4096 characters.
    """
    chunks = []
    current_chunk = []

    char_count = 0
    for line in lines:
        count = len(line)

        # We can add the line without exceeding the char limit.
        if count + char_count + 1 < MAX_LENGTH:
            char_count += count
            # We add another char for the newline
            char_count += 1
            current_chunk.append(line)

        # We exceed the max chunk size. Start a new chunk
        else:
            char_count = count
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]

            # We reached the max chunk size. Early return
            if len(chunks) == max_chunks:
                return chunks

    chunks.append('\n'.join(current_chunk))
    return chunks


def extract_from_result_id(result_id):
    """Extract default uuid string repr from compressed format."""
    delimiters = [8, 4, 4, 4, 12]
    uuid = 'urn:uuid:'
    for delimiter in delimiters:
        if uuid != 'urn:uuid:':
            uuid += '-'
        uuid += result_id[:delimiter]
        result_id = result_id[delimiter:]

    return uuid, result_id
