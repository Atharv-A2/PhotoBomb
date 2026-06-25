# import logging

# from app.db.session.worker_session import (
#     WorkerSessionLocal,
# )

# from app.db.repositories.Sync.worker_upload_session_repository import (
#     UploadSyncSessionRepository,
# )

# from app.workers.celery.app import (
#     celery_app,
# )

# logger = logging.getLogger(
#     __name__
# )


# @celery_app.task(
#     name="cleanup.upload_sessions"
# )

# def cleanup_upload_sessions():

#     with (
#         WorkerSessionLocal()
#         as session
#     ):
#         repo = (
#             UploadSyncSessionRepository(
#                 session
#             )
#         )

#         deleted_count = (
#             repo.delete_expired()
#         )

#         session.commit()

#         logger.info(
#             "Deleted %s expired upload sessions",
#             deleted_count,
#         )