from sqlalchemy import select

from app.db.models.upload_session import (
    UploadSession
)


class UploadSessionRepository:

    def __init__(
        self,
        session,
    ):
        self.session = session

    async def create(
        self,
        upload_session,
    ):
        self.session.add(
            upload_session
        )
        await self.session.flush()
        return upload_session

    async def get(
        self,
        upload_id,
    ):
        stmt = select(
            UploadSession
        ).where(
            UploadSession.id
            == upload_id
        )

        result = (
            await self.session.execute(
                stmt
            )
        )

        return (
            result.scalar_one_or_none()
        )