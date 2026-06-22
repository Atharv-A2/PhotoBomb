import logging

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
    logger.info(
        "Processing media %s",
        media_id,
    )

    return {
        "media_id": media_id,
        "status": "queued",
    }