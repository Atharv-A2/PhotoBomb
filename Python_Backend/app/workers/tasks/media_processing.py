import logging
from pathlib import Path

from app.db.repositories.media_repository import (
    MediaRepository,
)
from app.db.session.session import (
    AsyncSessionLocal,
)
from app.services.metadata.metadata_service import (
    MetadataService,
)
from app.workers.celery.app import (
    celery_app,
)

logger = logging.getLogger(
    __name__
)


@celery_app.task(
    name="media.process",
)
def process_media(
    media_id: str,
):
    import asyncio

    asyncio.run(
        process_media_async(
            media_id
        )
    )


async def process_media_async(
    media_id: str,
):
    async with (
        AsyncSessionLocal()
        as session
    ):
        repo = (
            MediaRepository(
                session
            )
        )

        media = (
            await repo.get(
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

        await (
            repo.update_metadata(
                media,
                metadata,
            )
        )

        await session.commit()

        logger.info(
            "Metadata extracted for %s",
            media_id,
        )