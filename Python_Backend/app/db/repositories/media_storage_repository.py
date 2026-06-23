from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.models.media_storage import (
    MediaStorage,
)


class MediaStorageRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_media_id(
        self,
        media_id,
    ):
        stmt = (
            select(
                MediaStorage
            )
            .where(
                MediaStorage.media_id
                == media_id
            )
        )

        result = (
            await self.session.execute(
                stmt
            )
        )

        return (
            result.scalar_one_or_none()
        )