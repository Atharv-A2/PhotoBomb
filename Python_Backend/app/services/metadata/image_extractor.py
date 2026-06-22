import json
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image


class ImageMetadataExtractor:

    def extract(
        self,
        path: Path,
    ):
        image = Image.open(path)

        width, height = image.size

        capture_time = (
            self._extract_capture_time(
                path
            )
        )

        return {
            "width": width,
            "height": height,
            "capture_time":
                capture_time,
        }

    def _extract_capture_time(
        self,
        path: Path,
    ):
        try:
            result = subprocess.run(
                [
                    "exiftool",
                    "-json",
                    str(path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            metadata = json.loads(
                result.stdout
            )[0]

            candidates = [
                "DateTimeOriginal",
                "CreateDate",
                "DateTimeDigitized",
                "ModifyDate",
            ]

            for field in candidates:
                value = metadata.get(
                    field
                )

                if not value:
                    continue

                try:
                    return datetime.strptime(
                        value,
                        "%Y:%m:%d %H:%M:%S",
                    )
                except ValueError:
                    pass

        except Exception:
            pass

        return None