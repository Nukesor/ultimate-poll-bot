"""Inline query handler function."""
import uuid

from sqlalchemy import or_
from sqlalchemy.orm.scoping import scoped_session
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.bot import Bot
from telegram.update import Update

from pollbot.config import config
from pollbot.enums import CallbackType, ReferenceType
from pollbot.i18n import i18n
from pollbot.models import Poll
from pollbot.models.user import User
from pollbot.telegram.session import inline_query_wrapper


@inline_query_wrapper
def search(bot: Bot, update: Update, session: scoped_session, user: User) -> None:
    """Handle inline queries for sticker search."""
    query = update.inline_query.query.strip()

    # Also search for closed polls if the `closed_polls` keyword is found
    closed = False
    if "closed_polls" in query:
        closed = True
        query = query.replace("closed_polls", "").strip()

    offset = update.inline_query.offset

    if offset == "":
        offset = 0
    elif offset == "Done":
        update.inline_query.answer(
            [],
            cache_time=0,
            is_personal=True,
        )
        return
    else:
        offset = int(offset)

    if query == "":
        # Just display all polls
        polls = (
            session.query(Poll)
            .filter(Poll.user == user)
            .filter(Poll.closed.is_(closed))
            .filter(Poll.created.is_(True))
            .filter(Poll.delete.is_(None))
            .order_by(Poll.created_at.desc())
            .limit(10)
            .offset(offset)
            .all()
        )

    else:
        # Find polls with search parameter in name or description
        polls = (
            session.query(Poll)
            .filter(Poll.user == user)
            .filter(Poll.closed.is_(closed))
            .filter(Poll.created.is_(True))
            .filter(Poll.delete.is_(None))
            .filter(
                or_(
                    Poll.name.ilike(f"%{query}%"),
                    Poll.description.ilike(f"%{query}%"),
                )
            )
            .order_by(Poll.created_at.desc())
            .limit(10)
            .offset(offset)
            .all()
        )

    # Try to find polls that are shared by external people via uuid
    if len(polls) == 0 and len(query) == 36:
        try:
            poll_uuid = uuid.UUID(query)
            poll = (
                session.query(Poll)
                .filter(Poll.uuid == poll_uuid)
                .filter(Poll.delete.is_(None))
                .offset(offset)
                .one_or_none()
            )

            if poll is not None:
                # Check if sharin is enabled
                # If not, check if the owner issued the query
                if not poll.allow_sharing and user != poll.user:
                    polls = []
                else:
                    polls = [poll]

        except ValueError:
            pass

    if len(polls) == 0:
        update.inline_query.answer(
            [],
            cache_time=0,
            is_personal=True,
        )
    else:
        results = []
        for poll in polls:
            inline_reference_count = 0
            for reference in poll.references:
                if reference.type == ReferenceType.inline.name:
                    inline_reference_count += 1

            max_share_amount = config["telegram"]["max_inline_shares"]
            if inline_reference_count > max_share_amount:
                text = i18n.t(
                    "poll.shared_too_often", locale=poll.locale, amount=max_share_amount
                )
                results.append(
                    InlineQueryResultArticle(
                        uuid.uuid4(),
                        poll.name,
                        description=text,
                        input_message_content=InputTextMessageContent(text),
                    )
                )
                continue

            text = i18n.t("poll.please_wait", locale=poll.locale)
            data = f"{CallbackType.update_shared.value}:{poll.id}:0"
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Not syncing? Try clicking", callback_data=data
                        )
                    ]
                ]
            )

            content = InputTextMessageContent(
                text,
                parse_mode="markdown",
                disable_web_page_preview=True,
            )
            description = (
                poll.description[:100] if poll.description is not None else None
            )
            results.append(
                InlineQueryResultArticle(
                    poll.id,
                    poll.name,
                    description=description,
                    input_message_content=content,
                    reply_markup=keyboard,
                )
            )

        if len(polls) < 10:
            offset = "Done"
        else:
            offset + 10

        update.inline_query.answer(
            results,
            cache_time=0,
            is_personal=True,
            next_offset=str(offset),
        )
