from time import sleep
from telegram.error import BadRequest, RetryAfter, Unauthorized
from sqlalchemy.orm.exc import ObjectDeletedError

from pollbot.enums import ReferenceType
from pollbot.i18n import i18n
from pollbot.poll.update import send_updates
from pollbot.sentry import sentry


def delete_poll(session, context, poll, remove_all=False):
    """Delete a poll.

    By default, the poll will simply be deleted from the database.
    If the poll wasn't closed yet, it will be closed and all messages will be
    updated once, to indicate that the poll is now closed.

    If remove_all is set to true , ALL poll messages will be removed.
    """
    # In case the poll messages should not be removed,
    # only close the poll and update the message, if necessary.
    if not remove_all:
        if not poll.closed:
            poll.closed = True
            try:
                send_updates(session, context.bot, poll)
            except RetryAfter as e:
                # In case we get an flood control error, wait a little longer
                # than the specified time. Afterwards, just try again.
                retry_after = int(e.retry_after) + 5
                sleep(retry_after)

                send_updates(session, context.bot, poll)

        session.delete(poll)
        return

    for reference in poll.references:
        try:
            # 1. Admin poll management interface
            # 2. User that votes in private chat (priority vote)
            if reference.type in [
                ReferenceType.admin.name,
                ReferenceType.private_vote.name,
            ]:
                context.bot.edit_message_text(
                    i18n.t("deleted.poll", locale=poll.locale),
                    chat_id=reference.user.id,
                    message_id=reference.message_id,
                )

            # Remove message created via inline_message_id
            else:
                context.bot.edit_message_text(
                    i18n.t("deleted.poll", locale=poll.locale),
                    inline_message_id=reference.bot_inline_message_id,
                )

            # Early delete of the reference
            # If something critical, such as a flood control error, happens in the middle
            # of a delete, we don't have to update all previous references again.
            session.delete(reference)
            session.flush()
        except RetryAfter as e:
            # In case we get an flood control error, wait for the specified time
            # Then rollback the transaction, and return. The reference will then be updated
            # the next time the job runs.
            retry_after = int(e.retry_after) + 5
            sleep(retry_after)
            session.rollback()
            return

        except BadRequest as e:
            if (
                e.message.startswith("Message_id_invalid")
                or e.message.startswith("Have no rights to send a message")
                or e.message.startswith("Message is not modified")
                or e.message.startswith("Message to edit not found")
                or e.message.startswith("Message identifier is not specified")
                or e.message.startswith("Chat_write_forbidden")
                or e.message.startswith("Chat not found")
            ):
                pass
            else:
                # Don't die if a single poll fails.
                # Otherwise all other users get stuck as well.
                if should_report_exception(context, e):
                    sentry.capture_exception(tags={"handler": "job"})
                return
        except Unauthorized:
            pass
        except ObjectDeletedError:
            # This reference has already been deleted somewhere else. Just ignore this.
            pass

    session.delete(poll)
    session.flush()
