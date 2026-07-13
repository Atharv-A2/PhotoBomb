import logging
from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_shutdown

from app.services.storage.factory import StorageProviderFactory
from app.db.enums.storage_provider_type import (
    StorageProviderType,
)

from app.core.config.settings import (
    get_settings,
)

from celery.signals import (
    worker_process_init,
    worker_process_shutdown,
)

from app.providers.telegram.lifecycle import (
    TelegramLifecycle,
)


logger = logging.getLogger(__name__)

settings = get_settings()

celery_app = Celery(
    "photobomb",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    imports=(
        "app.workers.tasks.media_processing",
        "app.workers.tasks.session_cleanup",
    ),
)


# celery_app.conf.beat_schedule = {
#     "cleanup-expired-upload-sessions": {
#         "task": "cleanup.upload_sessions",
#         "schedule": crontab(
#             minute=0,
#         ),
#     },
# }

from datetime import timedelta

celery_app.conf.beat_schedule = {
    "cleanup-expired-upload-sessions": {
        "task": "cleanup.upload_sessions",
        "schedule": timedelta(
            minutes=1
        ),
    },
}

@worker_shutdown.connect
def shutdown_storage(**kwargs):
    provider = StorageProviderFactory.get(
        StorageProviderType.TELEGRAM
    )

    provider.shutdown()


###########################################################################
# Telegram Lifecycle
###########################################################################


# @worker_process_init.connect
# def initialize_telegram(**kwargs):
#     """
#     Runs once for every Celery worker process.

#     Creates:

#         - Event Loop
#         - Telethon Client
#         - Telegram Service

#     before any task starts.
#     """

#     logger.info(
#         "Initializing Telegram client..."
#     )

#     TelegramClientManager.instance().start()

#     logger.info(
#         "Telegram client initialized."
#     )


# @worker_process_shutdown.connect
# def shutdown_telegram(**kwargs):
#     """
#     Gracefully disconnect Telethon when
#     the worker exits.
#     """

#     logger.info(
#         "Stopping Telegram client..."
#     )

#     TelegramClientManager.instance().shutdown()

#     logger.info(
#         "Telegram client stopped."
#     )


@worker_process_init.connect
def telegram_worker_start(
    **kwargs,
):
    """
    Executed once for every Celery worker process.

    Creates exactly one Telegram transport and one
    Telethon client for this process.
    """

    logger.info(
        "Starting Telegram transport..."
    )

    TelegramLifecycle.instance().start()

    logger.info(
        "Telegram transport started."
    )


@worker_process_shutdown.connect
def telegram_worker_shutdown(
    **kwargs,
):
    """
    Gracefully shutdown the Telegram transport before
    the worker process exits.
    """

    logger.info(
        "Stopping Telegram transport..."
    )

    TelegramLifecycle.instance().shutdown()

    logger.info(
        "Telegram transport stopped."
    )