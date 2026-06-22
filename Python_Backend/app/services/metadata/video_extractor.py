import json
import subprocess
from datetime import datetime
from pathlib import Path

from app.core.config.settings import (
    get_settings,
)

settings = get_settings()


class VideoMetadataExtractor:

    def extract(
        self,
        path: Path,
    ):
        command = [
            settings.ffprobe_binary,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        metadata = json.loads(
            result.stdout
        )

        width = None
        height = None
        duration = None
        capture_time = None

        for stream in metadata.get(
            "streams",
            [],
        ):
            if (
                stream.get(
                    "codec_type"
                )
                == "video"
            ):
                width = stream.get(
                    "width"
                )

                height = stream.get(
                    "height"
                )

                duration_str = (
                    stream.get(
                        "duration"
                    )
                )

                if duration_str:
                    duration = float(
                        duration_str
                    )

                tags = stream.get(
                    "tags",
                    {}
                )

                capture_time = (
                    self._parse_date(
                        tags
                    )
                )

                break

        if duration is None:
            format_data = metadata.get(
                "format",
                {}
            )

            duration_str = (
                format_data.get(
                    "duration"
                )
            )

            if duration_str:
                duration = float(
                    duration_str
                )

            if capture_time is None:
                capture_time = (
                    self._parse_date(
                        format_data.get(
                            "tags",
                            {}
                        )
                    )
                )

        return {
            "width": width,
            "height": height,
            "duration":
                duration,
            "capture_time":
                capture_time,
        }

    def _parse_date(
        self,
        tags,
    ):
        candidates = [
            "creation_time",
            "com.apple.quicktime.creationdate",
            "CreationTime",
        ]

        for field in candidates:
            value = tags.get(
                field
            )

            if not value:
                continue

            try:
                return datetime.fromisoformat(
                    value.replace(
                        "Z",
                        "+00:00",
                    )
                )
            except Exception:
                pass

        return None