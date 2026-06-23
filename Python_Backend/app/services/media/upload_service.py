from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from fastapi import UploadFile
import secrets

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.enums.upload_status import (
    UploadStatus,
)
from app.db.models.upload_session import (
    UploadSession,
)
from app.db.repositories.upload_session_repository import (
    UploadSessionRepository,
)
from app.schemas.media.request import (
    CreateUploadSessionRequest,
)
from app.schemas.media.response import (
    UploadSessionResponse,
)
from app.services.media.validators import (
    validate_mime_type,
)

from app.core.config.settings import (
    get_settings,
)
from app.db.enums.media_status import (
    MediaStatus,
)
from app.db.enums.media_type import (
    MediaType,
)
from app.db.models.media import Media
from app.db.repositories.media_repository import (
    MediaRepository,
)
from app.services.media.storage_service import (
    TemporaryStorageService,
)
from app.utils.file_utils import (
    build_temp_path, move_file
)
from app.workers.tasks.media_processing import (
    process_media,
)
from app.services.media.file_detector import (
    FileDetector,
)

settings = get_settings()


class UploadService:

    def __init__(
        self,
        session,
    ):
        self.session = session

        self.upload_sessions = (
            UploadSessionRepository(
                session
            )
        )

        self.media = (
            MediaRepository(
                session
            )
        )

        self.storage = (
            TemporaryStorageService()
        )

    async def create_upload_session(
        self,
        user_id,
        request:
            CreateUploadSessionRequest,
    ):
        validate_mime_type(
            request.mime_type
        )

        upload_session = (
            UploadSession(
                user_id=user_id,
                upload_token=(
                    secrets.token_urlsafe(
                        32
                    )
                ),
                filename=request.filename,
                mime_type=request.mime_type,
                file_size=request.file_size,
                status=(
                    UploadStatus.PENDING
                ),
                expires_at=(
                    datetime.now(UTC)
                    + timedelta(
                        hours=1
                    )
                ),
            )
        )

        await (
            self.upload_sessions
            .create(
                upload_session
            )
        )

        await self.session.commit()

        await self.session.refresh(
            upload_session
        )

        return (
            UploadSessionResponse(
                upload_session_id=
                    upload_session.id,
                status=
                    upload_session.status,
            )
        )
    

    async def upload_file(
        self,
        upload_session_id,
        user_id,
        file: UploadFile,
    ):
        upload_session = (
            await self.upload_sessions.get(
                upload_session_id
            )
        )

        if upload_session is None:
            raise ValueError(
                "Upload session not found"
            )

        if (
            upload_session.user_id
            != user_id
        ):
            raise ValueError(
                "Upload session not found"
            )

        await (
            self.upload_sessions
            .update_status(
                upload_session,
                UploadStatus.UPLOADING,
            )
        )

        incoming_root = (
            settings.temp_storage_path
        )

        incoming_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_path = build_temp_path(
            incoming_root,
            ".upload",
        )

        await self.storage.save(
            file,
            temp_path,
        )

        actual = FileDetector.detect(temp_path)

        actual_mime_type = (actual["mime_type"])

        if actual_mime_type.startswith(
            "image/"
        ):
            media_type = (MediaType.IMAGE)

        elif actual_mime_type.startswith(
            "video/"
        ):
            media_type = (MediaType.VIDEO)

        else:
            raise ValueError("Unsupported file type")
        
        root = (
            settings.temp_storage_path
            / (
                "images"
                if media_type
                == MediaType.IMAGE
                else "videos"
            )
        )

        extension = (
            f".{actual['extension']}"
        )

        final_path = (
            build_temp_path(
                root,
                extension,
            )
        )

        move_file(
            temp_path,
            final_path,
        )

        media = Media(
            user_id=user_id,
            media_type=media_type,
            status=(
                MediaStatus
                .UPLOADED_TEMP
            ),
            original_filename=(
                upload_session.filename
            ),
            mime_type=(
                actual_mime_type
            ),
            file_size=(
                final_path.stat().st_size
            ),
            temp_path=str(
                final_path
            ),
        )

        await self.media.create(
            media
        )

        await (
            self.upload_sessions
            .update_status(
                upload_session,
                UploadStatus.PROCESSING,
            )
        )

        await self.session.commit()
        
        process_media.delay(
            str(media.id)
        )

        await self.session.refresh(
            media
        )

        return {
            "media_id":
                str(media.id),
            "status":
                media.status,
        }
    

    async def create_bulk_upload_sessions(
        self,
        user_id,
        requests,
    ):
        MAX_BULK_SESSION_SIZE = 1000
        
        sessions = []

        for request in requests:

            validate_mime_type(
                request.mime_type
            )

            upload_session = (
                UploadSession(
                    user_id=user_id,
                    upload_token=(
                        secrets.token_urlsafe(
                            32
                        )
                    ),
                    filename=(
                        request.filename
                    ),
                    mime_type=(
                        request.mime_type
                    ),
                    file_size=(
                        request.file_size
                    ),
                    status=(
                        UploadStatus.PENDING
                    ),
                    expires_at=(
                        datetime.now(
                            UTC
                        )
                        + timedelta(
                            hours=1
                        )
                    ),
                )
            )

            await (
                self.upload_sessions
                .create(
                    upload_session
                )
            )

            sessions.append(
                upload_session
            )

        await self.session.commit()

        responses = []

        for session in sessions:
            responses.append(
                UploadSessionResponse(
                    upload_session_id=
                        session.id,
                    status=
                        session.status,
                )
            )

        return responses