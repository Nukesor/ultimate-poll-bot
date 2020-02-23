"""Inline query handler function."""
import uuid
from telethon import events, Button
from telethon.tl.types import InputWebDocument
from sqlalchemy import or_

from pollbot.i18n import i18n
from pollbot.models import Poll
from pollbot.client import client
from pollbot.display.poll.compilation import get_poll_text_and_vote_keyboard
from pollbot.helper.session import inline_query_wrapper


@client.on(events.InlineQuery)
@inline_query_wrapper
async def search(session, event, user):
    """Handle inline queries for sticker search."""
    query = event.query.query.strip()
    builder = event.builder

    # Also search for closed polls if the `closed_polls` keyword is found
    closed = False
    if 'closed_polls' in query:
        closed = True
        query = query.replace('closed_polls', '').strip()

    offset = event.query.offset

    if offset == '':
        offset = 0
    else:
        offset = int(offset)

    if query == '':
        # Just display all polls
        polls = session.query(Poll) \
            .filter(Poll.user == user) \
            .filter(Poll.closed.is_(closed)) \
            .filter(Poll.created.is_(True)) \
            .order_by(Poll.created_at.desc()) \
            .limit(10) \
            .offset(offset) \
            .all()

    else:
        # Find polls with search parameter in name or description
        polls = session.query(Poll) \
            .filter(Poll.user == user) \
            .filter(Poll.closed.is_(closed)) \
            .filter(Poll.created.is_(True)) \
            .filter(or_(
                Poll.name.ilike(f'%{query}%'),
                Poll.description.ilike(f'%{query}%'),
            )) \
            .order_by(Poll.created_at.desc()) \
            .limit(10) \
            .offset(offset) \
            .all()

    # Try to find polls that are shared by external people via uuid
    if len(polls) == 0 and len(query) == 36:
        try:
            poll_uuid = uuid.UUID(query)
            polls = session.query(Poll) \
                .filter(Poll.uuid == poll_uuid) \
                .all()
        except ValueError:
            pass

    if len(polls) == 0:
        await event.answer([], cache_time=0, private=True)
    else:
        results = []
        for poll in polls:
            inline_reference_count = 0
            for reference in poll.references:
                if reference.inline_message_id is not None:
                    inline_reference_count += 1

            if inline_reference_count > 20:
                continue

            text, keyboard = get_poll_text_and_vote_keyboard(
                session, poll,
                user=user,
                inline_query=True
            )
            keyboard = [[Button.inline('Please ignore this', data='100:0:0')]]

            description = poll.description[:100] if poll.description is not None else None
            results.append(builder.article(
                poll.name,
                text=text,
                description=description,
                id=str(poll.id),
                buttons=keyboard,
                link_preview=False,
            ))

        await event.answer(
            results,
            cache_time=0,
            private=True,
            next_offset=str(offset+10),
        )
