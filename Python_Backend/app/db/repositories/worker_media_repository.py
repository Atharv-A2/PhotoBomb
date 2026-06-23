from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.media import Media
from app.db.enums.media_status import (
    MediaStatus,
)


class WorkerMediaRepository:

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def get(self, media_id):
        stmt = select(Media).where(
            Media.id == media_id
        )

        result = self.session.execute(stmt)

        return result.scalar_one_or_none()

    def update_metadata(
        self,
        media,
        metadata,
    ):
        media.width = metadata.get("width")
        media.height = metadata.get("height")
        media.duration = metadata.get("duration")
        media.capture_time = metadata.get(
            "capture_time"
        )

        self.session.flush()

        return media

    def create(self, media):
        self.session.add(media)
        self.session.flush()

        return media
    
    def update_status(
        self,
        media,
        status: MediaStatus,
    ):
        media.status = status

        self.session.flush()

        return media