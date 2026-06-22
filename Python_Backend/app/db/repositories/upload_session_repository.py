from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.models.upload_session import (
    UploadSession,
)


class UploadSessionRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        upload_session: UploadSession,
    ):
        self.session.add(
            upload_session
        )

        await self.session.flush()

        return upload_session

    async def get(
        self,
        upload_session_id,
    ):
        stmt = select(
            UploadSession
        ).where(
            UploadSession.id
            == upload_session_id
        )

        result = (
            await self.session.execute(
                stmt
            )
        )

        return (
            result.scalar_one_or_none()
        )