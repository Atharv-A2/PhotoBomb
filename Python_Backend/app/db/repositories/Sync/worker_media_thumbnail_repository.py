from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.media_thumbnail import (
    MediaThumbnail,
)
class WorkerMediaThumbnailRepository:

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def create(
            self, 
            thumbnail: MediaThumbnail
    ):
        self.session.add(thumbnail)
        self.session.flush()

        return thumbnail
    
    
    def get_by_media_id(
        self,
        media_id,
    ):
        stmt = select(
            MediaThumbnail
        ).where(
            MediaThumbnail.media_id
            == media_id
        )

        result = self.session.execute(
            stmt
        )

        return (
            result.scalar_one_or_none()
        )