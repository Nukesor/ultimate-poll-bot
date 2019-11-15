"""Inline query handler function."""
import uuid
from sqlalchemy import or_
from telegram.ext import run_async
from telegram import (
    InlineQueryResultArticle,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputTextMessageContent,
)

from pollbot.i18n import i18n
from pollbot.models import Poll
from pollbot.display import get_poll_text_and_vote_keyboard
from pollbot.helper.session import hidden_session_wrapper


@run_async
@hidden_session_wrapper()
def search(bot, update, session, user):
    """Handle inline queries for sticker search."""
    query = update.inline_query.query.strip()

    # Also search for closed polls if the `closed_polls` keyword is found
    closed = False
    if 'closed_polls' in query:
        closed = True
        query = query.replace('closed_polls', '').strip()

    offset = update.inline_query.offset

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
            print('geilo')
            pass

    if len(polls) == 0:
        update.inline_query.answer(
            [], cache_time=0, is_personal=True,
            switch_pm_text=i18n.t('inline_query.create_first', locale=user.locale),
            switch_pm_parameter='inline',
        )
    else:
        results = []
        for poll in polls:
            text, keyboard = get_poll_text_and_vote_keyboard(
                session, poll,
                user=user,
                inline_query=True
            )
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Please ignore this', callback_data='100')]])

            content = InputTextMessageContent(
                text,
                parse_mode='markdown',
                disable_web_page_preview=True,
            )
            description = poll.description[:100] if poll.description is not None else None
            results.append(InlineQueryResultArticle(
                poll.id,
                poll.name,
                description=description,
                input_message_content=content,
                reply_markup=keyboard,
            ))

        update.inline_query.answer(
            results, cache_time=0, is_personal=True,
            switch_pm_text=i18n.t('inline_query.create_poll', locale=user.locale),
            switch_pm_parameter='inline',
            next_offset=str(offset+10),
        )
