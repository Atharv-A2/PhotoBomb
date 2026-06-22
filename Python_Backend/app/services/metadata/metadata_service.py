from pathlib import Path

from app.db.enums.media_type import (
    MediaType,
)
from app.services.metadata.image_extractor import (
    ImageMetadataExtractor,
)
from app.services.metadata.video_extractor import (
    VideoMetadataExtractor,
)


class MetadataService:

    def __init__(
        self,
    ):
        self.image = (
            ImageMetadataExtractor()
        )

        self.video = (
            VideoMetadataExtractor()
        )

    def extract(
        self,
        media_type,
        path: Path,
    ):
        if (
            media_type
            == MediaType.IMAGE
        ):
            return (
                self.image.extract(
                    path
                )
            )

        return self.video.extract(
            path
        )