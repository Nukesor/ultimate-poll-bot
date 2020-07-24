from pollbot.i18n import i18n


def poll_required(function):
    """Return if the poll does not exist in the context object."""

    def wrapper(session, context):
        if context.poll is None:
            return i18n.t("callback.poll_no_longer_exists", locale=context.user.locale)

        return function(session, context, context.poll)

    return wrapper
