from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.enums.media_type import (
    MediaType,
)


class GalleryItemResponse(
    BaseModel
):
    id: UUID

    media_type: MediaType

    thumbnail_id: UUID | None

    capture_time: (
        datetime | None
    )

    width: int | None

    height: int | None



class GalleryResponse(
    BaseModel
):
    items: list[
        GalleryItemResponse
    ]