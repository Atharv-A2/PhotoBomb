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
    

    def stream_file(
        self,
        storage_metadata: dict,
    ):
        file = self.client.get_file(
            storage_metadata["file_id"]
        )

        return self.client.stream_file(
            file["file_path"]
        )
    

    def download_to_path(
        self,
        storage_metadata,
        destination,
    ):

        file = self.client.get_file(
            storage_metadata[
                "file_id"
            ]
        )

        return self.client.download_to_path(
            file["file_path"],
            destination,
        )