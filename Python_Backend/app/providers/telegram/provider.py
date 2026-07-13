from __future__ import annotations

from pathlib import Path
from typing import AsyncGenerator

from app.providers.telegram.mapper import (
    TelegramMapper,
)

from app.providers.telegram.models import (
    TelegramRange,
)

from app.providers.telegram.transport import (
    TelegramTransport,
)

from app.services.storage.base import (
    StorageProvider,
)

from app.core.config.settings import get_settings
settings = get_settings()


class TelegramProvider(
    StorageProvider,
):

    def __init__(self):

        self.transport = (
            TelegramTransport()
        )

    ####################################################################
    # Lifecycle
    ####################################################################

    def start(
        self,
    ) -> None:

        self.transport.start()

    def shutdown(
        self,
    ) -> None:

        self.transport.shutdown()

    ####################################################################
    # Upload
    ####################################################################

    def upload_file(
        self,
        path: Path,
        media_type,
    ):
        
        chat_id = settings.telegram_media_chat_id

        media = self.transport.upload(
            chat_id=int(chat_id),
            path=path,
        )

        return TelegramMapper.to_upload_result(
            media
        )

    ####################################################################
    # Download
    ####################################################################

    def download_to_path(
        self,
        storage_metadata,
        destination: Path,
    ):

        media = (
            TelegramMapper.from_storage(
                storage_metadata
            )
        )

        return self.transport.download_to_path(

            media,

            destination,
        )

    ####################################################################
    # Streaming
    ####################################################################

    async def stream_file(
        self,
        storage_metadata,
        byte_range: TelegramRange,
    ) -> AsyncGenerator[
        bytes,
        None,
    ]:

        media = (
            TelegramMapper.from_storage(
                storage_metadata
            )
        )

        async for chunk in self.transport.stream(

            media,

            byte_range,
        ):

            yield chunk

    ####################################################################
    # Delete
    ####################################################################

    def delete_file(
        self,
        storage_metadata,
    ) -> None:

        media = (
            TelegramMapper.from_storage(
                storage_metadata
            )
        )

        self.transport.delete(
            media
        )