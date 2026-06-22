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
    build_temp_path,
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

        is_image = (
            upload_session.mime_type
            .startswith(
                "image/"
            )
        )

        media_type = (
            MediaType.IMAGE
            if is_image
            else MediaType.VIDEO
        )

        root = (
            settings
            .temp_storage_path
            / (
                "images"
                if is_image
                else "videos"
            )
        )

        extension = (
            Path(
                upload_session.filename
            )
            .suffix
        )

        temp_path = (
            build_temp_path(
                root,
                extension,
            )
        )
        print(settings.temp_storage_path)
        print(temp_path)
        print(temp_path.resolve())

        await self.storage.save(
            file,
            temp_path,
        )
        print("exists:", temp_path.exists())
        print("size:", temp_path.stat().st_size)

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
                upload_session.mime_type
            ),
            file_size=(
                upload_session.file_size
            ),
            temp_path=str(
                temp_path
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

        await self.session.refresh(
            media
        )

        return {
            "media_id":
                str(media.id),
            "status":
                media.status,
        }