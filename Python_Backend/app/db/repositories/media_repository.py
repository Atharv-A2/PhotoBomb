from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.models.media import Media


class MediaRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        media: Media,
    ):
        self.session.add(
            media
        )

        await self.session.flush()

        return media

    async def get(
        self,
        media_id,
    ):
        stmt = select(
            Media
        ).where(
            Media.id == media_id
        )

        result = (
            await self.session.execute(
                stmt
            )
        )

        return (
            result.scalar_one_or_none()
        )
    

    async def update_metadata(
        self,
        media,
        metadata: dict,
    ):
        media.width = metadata.get(
            "width"
        )

        media.height = metadata.get(
            "height"
        )

        media.duration = metadata.get(
            "duration"
        )

        media.capture_time = (
            metadata.get(
                "capture_time"
            )
        )

        await self.session.flush()