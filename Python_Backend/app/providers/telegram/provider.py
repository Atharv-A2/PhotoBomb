from pathlib import Path

from app.core.config.settings import (
    get_settings,
)
from app.providers.telegram.client import (
    TelegramClient,
)
from app.providers.telegram.mapper import (
    TelegramMapper,
)
from app.services.storage.base import (
    StorageProvider,
)

settings = get_settings()


class TelegramProvider(
    StorageProvider
):

    def __init__(self):
        self.client = (
            TelegramClient()
        )

    def upload_file(
        self,
        path: Path,
        media_type,
    ):
        result = (
            self.client.send_document(
                settings.telegram_media_chat_id,
                path,
            )
        )

        return (
            TelegramMapper
            .to_upload_result(
                result
            )
        )

    def download_file(
        self,
        storage_metadata,
    ):
        raise NotImplementedError

    def delete_file(
        self,
        storage_metadata,
    ):
        raise NotImplementedError