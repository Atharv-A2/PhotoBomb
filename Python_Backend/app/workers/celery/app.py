from celery import Celery
from celery.schedules import crontab

from app.core.config.settings import (
    get_settings,
)

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