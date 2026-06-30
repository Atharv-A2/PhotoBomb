from fastapi import Response
from pathlib import Path
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

from app.core.config.settings import (
    get_settings,
)

from app.db.repositories.media_repository import (
    MediaRepository,
)

from app.db.repositories.media_storage_repository import (
    MediaStorageRepository,
)

from app.schemas.media.viewer import (
    ViewerResponse,
)
from app.schemas.media.detail import (
    MediaDetailResponse,
)
from app.db.repositories.media_thumbnail_repository import (
    MediaThumbnailRepository,
)
from app.services.storage.storage_service import (
    StorageService,
)
from app.services.cache.cache_service import (
    CacheService,
)
from app.providers.telegram.client import (
    TelegramClient
)
from app.services.streaming.range_stream import (
    RangeStream,
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
        
        self.thumbnail_repo = (
            MediaThumbnailRepository(
                session
            )
        )

        self.storage_service = StorageService()

        self.telegram = TelegramClient()

        self.cache = CacheService()

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
        request: Request
    ):
        media = await self.media.get(
            media_id
        )

        if media is None:
            raise ValueError(
                "Media not found"
            )

        storage = await (
            self.storage.get_by_media_id(
                media_id
            )
        )

        if storage is None:
            raise ValueError(
                "Storage not found"
            )
        
        extension = Path(
            media.original_filename
        ).suffix

        cached_path = (
            self.cache.get_cached_path(
                storage.storage_key,
                extension,
            )
        )

        if not cached_path.exists():

            self.storage_service.download_to_path(
                storage.storage_metadata,
                cached_path,
            )

        file_size = (
            cached_path.stat().st_size
        )

        range_header = request.headers.get("range")

        if range_header:

            start, end = RangeStream.parse_range(
                range_header,
                file_size,
            )

            headers = {
                "Accept-Ranges": "bytes",
                "Content-Length": str(end - start + 1),
                "Content-Range":
                    f"bytes {start}-{end}/{file_size}",
            }

            return StreamingResponse(
                RangeStream.stream(
                    cached_path,
                    start,
                    end,
                ),
                status_code=206,
                media_type=media.mime_type,
                headers=headers,
            )
        
        else: 
            return FileResponse(
                cached_path,
                media_type=media.mime_type,
            )
        

    async def get_thumbnail(
        self,
        thumbnail_id,
    ):
        thumbnail = await (
            self.thumbnail_repo.get(
                thumbnail_id
            )
        )

        if thumbnail is None:
            raise HTTPException(
                status_code=404,
                detail="Thumbnail not found",
            )
        
        path = Path(
            thumbnail.path
        )

        if not path.exists():
            raise HTTPException(
                status_code=404,
                detail="Thumbnail not found"
            )

        return FileResponse(
            path,
            media_type="image/webp",
        )