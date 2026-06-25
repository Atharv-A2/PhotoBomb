from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.upload_session import (
    UploadSession,
)


class WorkerUploadSessionRepository:

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def get(
        self,
        upload_session_id,
    ):
        stmt = select(
            UploadSession
        ).where(
            UploadSession.id
            == upload_session_id
        )

        result = self.session.execute(
            stmt
        )

        return (
            result.scalar_one_or_none()
        )

    def delete(
        self,
        upload_session: UploadSession,
    ):
        self.session.delete(
            upload_session
        )

        self.session.flush()