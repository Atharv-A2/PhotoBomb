from pathlib import Path
from uuid import uuid4

from app.db.enums.media_type import (
    MediaType,
)
from app.services.thumbnails.image_thumbnail_service import (
    ImageThumbnailService,
)
from app.services.thumbnails.video_thumbnail_service import (
    VideoThumbnailService,
)


class ThumbnailService:

    def __init__(
        self,
    ):
        self.image = (
            ImageThumbnailService()
        )

        self.video = (
            VideoThumbnailService()
        )

    def generate(
        self,
        media_type,
        source: Path,
        root: Path,
    ):
        filename = (
            f"{uuid4()}.webp"
        )

        destination = (
            root / filename
        )

        if (
            media_type
            == MediaType.IMAGE
        ):
            self.image.generate(
                source,
                destination,
            )
        else:
            self.video.generate(
                source,
                destination,
            )

        return destination