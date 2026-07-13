from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__)
        .resolve()
        .parents[2]
    )
)

from app.core.config.settings import get_settings

settings = get_settings()

API_ID = settings.telegram_api_id
API_HASH = settings.telegram_api_hash

with TelegramClient(
    StringSession(),
    API_ID,
    API_HASH,
) as client:

    print()

    print(client.session.save())

    print()