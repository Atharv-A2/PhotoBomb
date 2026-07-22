from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.db.repositories.media_repository import MediaRepository
from app.db.repositories.media_storage_repository import MediaStorageRepository
from app.services.storage.storage_service import StorageService


class DownloadService:

    def __init__(
        self,
        session,
    ):

        self._storage = StorageService()

        self._media_repo = MediaRepository(session)

        self._media_storage_repo = MediaStorageRepository(session)

    async def download_media(
        self,
        media_id: str,
    ) -> StreamingResponse:

        media = await self._media_repo.get(
            media_id
        )

        if media is None:

            raise HTTPException(

                status_code=404,

                detail="Media not found",
            )
        
        storage = await self._media_storage_repo.get_by_media_id(
            media_id
        )

        stream = self._storage.download_file(
            storage.storage_metadata
        )

        headers = {

            "Content-Disposition":
                f'attachment; filename="{media.original_filename}"',

            "Content-Length":
                str(media.file_size)
        }

        return StreamingResponse(

            stream,

            media_type=media.mime_type,

            headers=headers,
        )