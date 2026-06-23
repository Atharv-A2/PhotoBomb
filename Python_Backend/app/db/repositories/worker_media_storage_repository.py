from sqlalchemy.orm import Session
from app.db.models.media_storage import (
    MediaStorage,
)


class WorkerMediaStorageRepository:

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def create(
        self,
        media_storage:
            MediaStorage,
    ):
        self.session.add(
            media_storage
        )

        self.session.flush()

        return media_storage