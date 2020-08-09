from pollbot.enums import ReferenceType
from pollbot.i18n import i18n
from pollbot.poll.update import send_updates
from telegram.error import BadRequest


def remove_poll_messages(session, bot, poll, remove_all=False):
    """Remove all messages (references) of a poll."""
    # In case the poll messages should not be removed,
    # only close the poll and update the message, if necessary.
    if not remove_all:
        if not poll.closed:
            poll.closed = True
            send_updates(session, bot, poll)
        return

    for reference in poll.references:
        try:
            # 1. Admin poll management interface
            # 2. User that votes in private chat (priority vote)
            if reference.type in [
                ReferenceType.admin.name,
                ReferenceType.private_vote.name,
            ]:
                bot.edit_message_text(
                    i18n.t("deleted.poll", locale=poll.locale),
                    chat_id=reference.user.id,
                    message_id=reference.message_id,
                )

            # Remove message created via inline_message_id
            else:
                bot.edit_message_text(
                    i18n.t("deleted.poll", locale=poll.locale),
                    inline_message_id=reference.bot_inline_message_id,
                )

        except BadRequest as e:
            if e.message.startswith("Message_id_invalid") or e.message.startswith(
                "Message to edit not found"
            ):
                pass
            else:
                raise e
