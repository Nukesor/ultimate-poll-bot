from telethon.errors.rpcerrorlist import (
    MessageIdInvalidError,
    MessageNotModifiedError,
)
from telethon.errors.rpcbaseerrors import (
    ForbiddenError,
)

from pollbot.client import client
from pollbot.models import Reference


async def remove_old_references(session, poll, user):
    """Remove old references in private chats."""
    references = session.query(Reference) \
        .filter(Reference.poll == poll) \
        .filter(Reference.user == user) \
        .all()

    for reference in references:
        try:
            await client.delete_messages(reference.user_id, reference.message_id)
        except MessageIdInvalidError:
            session.delete(reference)
        except ForbiddenError:
            session.delete(reference)
        except ValueError:
            # Could not find input entity
            session.delete(reference)
        session.delete(reference)
