from pollbot.config import config
from pollbot.i18n import i18n


def poll_required(function):
    """Return if the poll does not exist in the context object."""

    def wrapper(session, context):
        if context.poll is None or context.poll.delete is not None:
            return i18n.t("callback.poll_no_longer_exists", locale=context.user.locale)

        return function(session, context, context.poll)

    return wrapper


def admin_required(function):
    """Return if the poll does not exist in the context object."""

    def wrapper(bot, update, session, user):
        if user.username.lower() != config["telegram"]["admin"].lower():
            return i18n.t("admin.not_allowed", locale=user.locale)

        return function(bot, update, session, user)

    return wrapper
