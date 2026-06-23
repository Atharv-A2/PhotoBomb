from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.media_thumbnail import (
    MediaThumbnail,
)


class MediaThumbnailRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        thumbnail: MediaThumbnail,
    ):
        self.session.add(
            thumbnail
        )

        await self.session.flush()

        return thumbnail

    async def get_by_media_id(
        self,
        media_id,
    ):
        stmt = select(
            MediaThumbnail
        ).where(
            MediaThumbnail.media_id
            == media_id
        )

        result = await self.session.execute(
            stmt
        )

        return (
            result.scalar_one_or_none()
        )