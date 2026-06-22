from telegram import Bot

from app.core.config.settings import (
    get_settings,
)

settings = get_settings()


def get_telegram_bot() -> Bot:
    return Bot(
        token=settings.telegram_bot_token
    )