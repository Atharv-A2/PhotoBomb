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
from app.db.enums.media_status import (
    MediaStatus,
)
from app.services.storage.factory import (
    StorageProviderFactory,
)
from app.db.enums.storage_provider_type import (
    StorageProviderType,
)
from app.db.repositories.worker_media_storage_repository import (
    WorkerMediaStorageRepository,
)
from app.db.models.media_storage import (
    MediaStorage,
)
from app.db.repositories.worker_storage_provider_repository import (
    WorkerStorageProviderRepository,
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

            repo.update_status(
                media,
                MediaStatus
                .UPLOADING_TELEGRAM,
            )

            provider_repo = (
                WorkerStorageProviderRepository(
                    session
                )
            )

            provider = (
                provider_repo.get_active(
                    StorageProviderType
                    .TELEGRAM
                )
            )

            if provider is None:
                raise RuntimeError(
                    "Telegram provider "
                    "not configured"
                )
            
            storage_provider = (
                StorageProviderFactory.get(
                    provider.type
                )
            )

            upload_result = (
                storage_provider
                .upload_file(
                    Path(
                        media.temp_path
                    ),
                    media.media_type,
                )
            )

            repo_storage = (
                WorkerMediaStorageRepository(
                    session
                )
            )

            storage = MediaStorage(
                media_id=media.id,
                storage_provider_id=
                    provider.id,
                storage_key=
                    upload_result
                    .storage_key,
                storage_metadata=
                    upload_result
                    .metadata,
            )

            repo_storage.create(
                storage
            )

            repo.update_status(
                media,
                MediaStatus
                .AVAILABLE,
            )

            session.commit()

            logger.info(
                "Metadata extracted for %s",
                media_id,
            )

        except Exception as exc:

            logger.exception(
                "Media processing failed: %s",
                media_id,
            )

            session.rollback()

            failed_media = repo.get(
                media_id
            )

            if failed_media:
                repo.update_status(
                    failed_media,
                    MediaStatus.FAILED,
                )

                session.commit()

            raise