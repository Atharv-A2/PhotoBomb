from __future__ import annotations

from telethon.sessions import StringSession

from app.core.config.settings import (
    get_settings,
)

from app.providers.telegram.exceptions import (
    TelegramAuthenticationError,
)

settings = get_settings()


def create_session() -> StringSession:
    """
    Creates the Telethon StringSession.

    This is the ONLY place where the transport
    knows how sessions are created.
    """

    session = settings.telegram_string_session

    if not session:

        raise TelegramAuthenticationError(
            "TELEGRAM_STRING_SESSION is not configured."
        )

    return StringSession(session)