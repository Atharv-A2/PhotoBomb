import logging
from pathlib import Path

from app.db.repositories.media_repository import (
    MediaRepository,
)
from app.db.session.session import (
    AsyncSessionLocal,
)
from app.db.session.worker_session import (
    WorkerSessionLocal,
)
from app.services.metadata.metadata_service import (
    MetadataService,
)
from app.workers.celery.app import (
    celery_app,
)
from app.db.enums.thumbnail_type import (
    ThumbnailType,
)
from app.db.models.media_thumbnail import (
    MediaThumbnail,
)
from app.services.thumbnails.thumbnail_service import (
    ThumbnailService,
)
from app.db.repositories.worker_media_repository import (
    WorkerMediaRepository,
)
from app.db.repositories.worker_media_thumbnail_repository import (
    WorkerMediaThumbnailRepository,
)
from app.core.config.settings import (
    get_settings,
)

logger = logging.getLogger(
    __name__
)
settings = get_settings()


@celery_app.task(
    name="media.process",
)
def process_media(
    media_id: str,
):
    process_media_sync(
        media_id
    )


def process_media_sync(
    media_id: str,
):
    with (
        WorkerSessionLocal()
        as session
    ):
        try:
            repo = (
                WorkerMediaRepository(
                    session
                )
            )

            media = (
                repo.get(
                    media_id
                )
            )

            if media is None:
                logger.error(
                    "Media not found %s",
                    media_id,
                )
                return

            metadata_service = (
                MetadataService()
            )

            metadata = (
                metadata_service.extract(
                    media.media_type,
                    Path(
                        media.temp_path
                    ),
                )
            )

            
            repo.update_metadata(
                media,
                metadata,
            )
            

            thumbnail_service = (
                ThumbnailService()
            )

            root = (
                settings.thumbnail_storage_path
                / (
                    "images"
                    if media.media_type.value
                    == "IMAGE"
                    else "videos"
                )
            )

            thumbnail_path = (
                thumbnail_service.generate(
                    media.media_type,
                    Path(media.temp_path),
                    root,
                )
            )

            repo_thumbnail = (
                WorkerMediaThumbnailRepository(
                    session
                )
            )

            thumbnail = MediaThumbnail(
                media_id=media.id,
                thumbnail_type=(
                    ThumbnailType.IMAGE
                    if media.media_type.value
                    == "IMAGE"
                    else ThumbnailType.VIDEO_PREVIEW
                ),
                path=str(
                    thumbnail_path
                ),
                width=min(
                    media.width or 512,
                    512,
                ),
                height=min(
                    media.height or 512,
                    512,
                ),
                size_bytes=(
                    thumbnail_path.stat()
                    .st_size
                ),
            )

            repo_thumbnail.create(
                thumbnail
            )

            session.commit()

            logger.info(
                "Metadata extracted for %s",
                media_id,
            )

        except Exception:

            session.rollback()
            raise