"""Inline query handler function."""
from sqlalchemy import or_
from telegram.ext import run_async
from telegram import InlineQueryResultArticle, InputTextMessageContent

from pollbot.i18n import i18n
from pollbot.helper.display import get_poll_text
from pollbot.helper.session import hidden_session_wrapper
from pollbot.models import Poll
from pollbot.telegram.keyboard import get_vote_keyboard


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

    if query == '':
        # Just display all polls
        polls = session.query(Poll) \
            .filter(Poll.user == user) \
            .filter(Poll.closed.is_(closed)) \
            .filter(Poll.created.is_(True)) \
            .order_by(Poll.created_at.desc()) \
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
            .all()

    if len(polls) == 0:
        update.inline_query.answer(
            [], cache_time=0, is_personal=True,
            switch_pm_text=i18n.t('inline_query.create_first', locale=user.locale),
            switch_pm_parameter='inline',
        )
    else:
        results = []
        for poll in polls:
            text = get_poll_text(session, poll, show_warning=False)
            content = InputTextMessageContent(
                text,
                parse_mode='markdown',
                disable_web_page_preview=True,
            )
            results.append(InlineQueryResultArticle(
                poll.id,
                poll.name,
                description=poll.description,
                input_message_content=content,
                reply_markup=get_vote_keyboard(poll),
            ))

        update.inline_query.answer(
            results, cache_time=0, is_personal=True,
            switch_pm_text=i18n.t('inline_query.create_poll', locale=user.locale),
            switch_pm_parameter='inline'
        )
