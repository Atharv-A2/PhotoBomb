from app.db.repositories.media_repository import (
    MediaRepository,
)
from app.db.repositories.media_thumbnail_repository import (
    MediaThumbnailRepository,
)

from app.schemas.media.gallery import (
    GalleryItemResponse,
    GalleryResponse,
)


class GalleryService:

    def __init__(self, session):
        self.media = MediaRepository(session)
        self.thumbnail = MediaThumbnailRepository(session)

    async def list_media(
        self,
        user_id,
        limit,
        offset,
    ):
        rows = await self.media.list_available(
            user_id,
            limit,
            offset,
        )

        if not rows:
            return GalleryResponse(
                items=[]
            )

        media_ids = [
            media.id
            for media in rows
        ]

        thumbnails = await (
            self.thumbnail.get_by_media_ids(
                media_ids
            )
        )

        thumbnail_map = {
            t.media_id: t
            for t in thumbnails
        }

        items = []

        for media in rows:

            thumbnail = thumbnail_map.get(
                media.id
            )

            items.append(
                GalleryItemResponse(
                    id=media.id,
                    media_type=media.media_type,
                    thumbnail_id=(
                        thumbnail.id
                        if thumbnail
                        else None
                    ),
                    capture_time=media.capture_time,
                    width=media.width,
                    height=media.height,
                )
            )

        return GalleryResponse(
            items=items
        )