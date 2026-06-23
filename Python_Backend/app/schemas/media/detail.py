from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.enums.media_type import (
    MediaType,
)


class MediaDetailResponse(
    BaseModel
):
    id: UUID

    media_type: MediaType

    original_filename: str

    file_size: int

    width: int | None

    height: int | None

    duration: float | None

    capture_time: (
        datetime | None
    )