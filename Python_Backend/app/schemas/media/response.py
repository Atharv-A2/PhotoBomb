from pydantic import BaseModel
from uuid import UUID

from app.db.enums.upload_status import (
    UploadStatus,
)


class UploadSessionResponse(
    BaseModel
):
    upload_session_id: UUID
    status: UploadStatus