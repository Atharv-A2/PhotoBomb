from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.models.media import Media
from sqlalchemy import desc
from app.db.enums.media_status import (
    MediaStatus,
)


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


    async def list_available(
        self,
        user_id,
        limit: int,
        offset: int,
    ):
        stmt = (
            select(Media)
            .where(
                Media.user_id == user_id,
                Media.status
                == MediaStatus.AVAILABLE,
            )
            .order_by(
                desc(Media.capture_time).nulls_last(),
                desc(Media.created_at),
            )
            .limit(limit)
            .offset(offset)
        )

        result = (
            await self.session.execute(
                stmt
            )
        )

        return (
            result.scalars().all()
        )