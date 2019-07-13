"""User related callback handler."""
from pollbot.i18n import i18n


def change_user_language(session, context):
    """Open the language picker."""
    context.user.locale = context.action
    session.commit()
    context.query.message.edit_text(
        i18n.t('user.language_changed', locale=context.user.locale))
