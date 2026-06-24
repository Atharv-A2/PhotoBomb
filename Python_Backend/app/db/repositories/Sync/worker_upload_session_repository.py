from sqlalchemy import delete
from datetime import datetime
from datetime import UTC
from sqlalchemy.orm import Session

from app.db.models.upload_session import (
    UploadSession,
)


class UploadSyncSessionRepository:

    def __init__(
        self,
        session: Session,
    ):
        self.session = session


    def delete_expired(self):
        stmt = delete(
            UploadSession
        ).where(
            UploadSession.expires_at
            < datetime.now(
                UTC
            )
        )

        result = self.session.execute(
            stmt
        )

        return result.rowcount