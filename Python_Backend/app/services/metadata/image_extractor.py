import json
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image


class ImageMetadataExtractor:

    DATE_CANDIDATES = [
        # Original capture time (preferred)
        ("DateTimeOriginal", "OffsetTimeOriginal"),

        # Image creation time
        ("CreateDate", "OffsetTime"),

        # Digitization time
        ("DateTimeDigitized", "OffsetTimeDigitized"),

        # Common for HEIC/QuickTime
        ("MediaCreateDate", None),
        ("TrackCreateDate", None),

        # GPS timestamp
        ("GPSDateTime", None),

        # Editable metadata
        ("ModifyDate", "OffsetTime"),

        # Last resort
        ("FileCreateDate", None),
        ("FileModifyDate", None),
    ]

    def extract(
        self,
        path: Path,
    ):
        metadata = self._read_metadata(path)

        return {
            "width": metadata.get("ImageWidth"),
            "height": metadata.get("ImageHeight"),
            "capture_time": self._extract_capture_time(metadata),
        }
    

    def _read_metadata(
        self,
        path: Path,
    ):
        try:
            result = subprocess.run(
                [
                    "exiftool",
                    "-json",
                    "-n",
                    path.as_posix(),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            return json.loads(result.stdout)[0]
    
        except (
            subprocess.CalledProcessError,
            json.JSONDecodeError,
            FileNotFoundError,
        ) as exc:
            raise RuntimeError(
                f"Failed to read metadata from {path}"
            ) from exc
    

    def _extract_capture_time(
        self,
        metadata: dict,
    ):
        for field, offset_field in self.DATE_CANDIDATES:
            value = metadata.get(field)

            if not value:
                continue

            capture_time = self._parse_datetime(
                value=value,
                offset=(
                    metadata.get(offset_field)
                    if offset_field
                    else None
                ),
            )

            if capture_time is not None:
                return capture_time

        return None


    def _parse_datetime(
        self,
        value: str,
        offset: str | None,
    ):
        value = value.strip()

        # ISO-8601 (HEIC, QuickTime, etc.)
        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            pass

        # Standard EXIF
        try:
            dt = datetime.strptime(
                value,
                "%Y:%m:%d %H:%M:%S",
            )

            if offset:
                try:
                    return datetime.fromisoformat(
                        dt.strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        )
                        + offset
                    )
                except ValueError:
                    pass

            return dt

        except ValueError:
            return None