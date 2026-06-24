from fastapi import Response
from app.core.config.settings import (
    get_settings,
)

from app.db.repositories.media_repository import (
    MediaRepository,
)

from app.db.repositories.media_storage_repository import (
    MediaStorageRepository,
)

from app.providers.telegram.client import (
    TelegramClient,
)

from app.schemas.media.viewer import (
    ViewerResponse,
)

from app.schemas.media.detail import (
    MediaDetailResponse,
)

settings = get_settings()


class ViewerService:

    def __init__(
        self,
        session,
    ):
        self.media = (
            MediaRepository(
                session
            )
        )

        self.storage = (
            MediaStorageRepository(
                session
            )
        )

        self.telegram = (
            TelegramClient()
        )

    async def get_detail(
        self,
        media_id,
    ):
        media = (
            await self.media.get(
                media_id
            )
        )

        if media is None:
            raise ValueError(
                "Media not found"
            )

        return (
            MediaDetailResponse(
                id=media.id,
                media_type=
                    media.media_type,
                original_filename=
                    media.original_filename,
                file_size=
                    media.file_size,
                width=
                    media.width,
                height=
                    media.height,
                duration=
                    media.duration,
                capture_time=
                    media.capture_time,
            )
        )

    async def get_viewer(
        self,
        media_id,
    ):
        storage = (
            await self.storage
            .get_by_media_id(
                media_id
            )
        )

        if storage is None:
            raise ValueError(
                "Storage not found"
            )

        file_id = (
            storage
            .storage_metadata[
                "file_id"
            ]
        )

        telegram_file = (
            self.telegram
            .get_file(
                file_id
            )
        )

        download_url = (
            self.telegram
            .build_download_url(
                telegram_file[
                    "file_path"
                ]
            )
        )

        return ViewerResponse(
            download_url=
                download_url
        )
    

    async def stream_media(
        self,
        media_id,
    ):
        media = (
            await self.media.get(
                media_id
            )
        )

        if media is None:
            raise ValueError(
                "Media not found"
            )

        storage = (
            await self.storage
            .get_by_media_id(
                media_id
            )
        )

        file_id = (
            storage.storage_metadata[
                "file_id"
            ]
        )

        telegram_file = (
            self.telegram.get_file(
                file_id
            )
        )

        file_bytes = (
            self.telegram
            .download_bytes(
                telegram_file[
                    "file_path"
                ]
            )
        )

        return Response(
            content=file_bytes,
            media_type=
                media.mime_type,
        )