import json
import subprocess
from datetime import datetime
from pathlib import Path

from app.core.config.settings import (
    get_settings,
)

settings = get_settings()


class VideoMetadataExtractor:

    DATE_CANDIDATES = [
        "creation_time",
        "com.apple.quicktime.creationdate",
        "com.apple.quicktime.creation_time",
        "MediaCreateDate",
        "TrackCreateDate",
        "CreateDate",
        "CreationTime",
        "Encoded_Date",
        "Tagged_Date",
    ]

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
            "-show_entries",
            (
                "stream=codec_type,width,height,duration:"

                "stream_tags="
                "creation_time,"
                "com.apple.quicktime.creationdate,"
                "com.apple.quicktime.creation_time,"
                "CreationTime,"
                "CreateDate,"
                "MediaCreateDate,"
                "TrackCreateDate,"
                "Encoded_Date,"
                "Tagged_Date:"

                "format=duration:"

                "format_tags="
                "creation_time,"
                "com.apple.quicktime.creationdate,"
                "com.apple.quicktime.creation_time,"
                "CreationTime,"
                "CreateDate,"
                "MediaCreateDate,"
                "TrackCreateDate,"
                "Encoded_Date,"
                "Tagged_Date"
            ),
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

        video_stream = next(
            (
                stream
                for stream in metadata.get(
                    "streams",
                    [],
                )
                if stream.get(
                    "codec_type"
                )
                == "video"
            ),
            None,
        )

        if video_stream:
            width = video_stream.get(
                "width"
            )

            height = video_stream.get(
                "height"
            )

            duration_str = video_stream.get(
                "duration"
            )

            if duration_str:
                duration = float(
                    duration_str
                )

            capture_time = (
                self._parse_date(
                    video_stream.get(
                        "tags",
                        {},
                    )
                )
            )

        format_data = metadata.get(
            "format",
            {},
        )

        if duration is None:
            duration_str = format_data.get(
                "duration"
            )

            if duration_str is not None:
                duration = float(
                    duration_str
                )

        if capture_time is None:
            capture_time = self._parse_date(
                format_data.get(
                    "tags",
                    {},
                )
            )

        return {
            "width": width,
            "height": height,
            "duration": duration,
            "capture_time": capture_time,
        }
    
    def _parse_date(
        self,
        tags: dict,
    ):
        for field in self.DATE_CANDIDATES:
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
            except ValueError:
                continue

        return None