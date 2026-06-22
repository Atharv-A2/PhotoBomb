from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS


class ImageMetadataExtractor:

    def extract(
        self,
        path: Path,
    ):
        image = Image.open(
            path
        )

        width, height = (
            image.size
        )

        capture_time = None

        exif = image.getexif()

        if exif:
            for tag_id, value in (
                exif.items()
            ):
                tag = TAGS.get(
                    tag_id,
                    tag_id,
                )

                if (
                    tag
                    == "DateTimeOriginal"
                ):
                    try:
                        capture_time = (
                            datetime.strptime(
                                value,
                                "%Y:%m:%d %H:%M:%S",
                            )
                        )
                    except Exception:
                        pass

                    break

        return {
            "width": width,
            "height": height,
            "capture_time":
                capture_time,
        }