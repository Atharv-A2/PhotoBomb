from datetime import UTC
from datetime import datetime
from datetime import timedelta
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


class UploadService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
        self.upload_sessions = (
            UploadSessionRepository(
                session
            )
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