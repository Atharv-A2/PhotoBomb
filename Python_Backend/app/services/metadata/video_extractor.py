import json
import subprocess
from pathlib import Path


class VideoMetadataExtractor:

    def extract(
        self,
        path: Path,
    ):
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_streams",
                "-show_format",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        data = json.loads(result.stdout)

        video_stream = next(
            (
                stream
                for stream in data["streams"]
                if stream["codec_type"] == "video"
            ),
            None,
        )

        if video_stream is None:
            raise ValueError(
                "No video stream found"
            )

        width = video_stream.get(
            "width"
        )

        height = video_stream.get(
            "height"
        )

        duration = float(
            data["format"]["duration"]
        )

        return {
            "width": width,
            "height": height,
            "duration": duration,
            "capture_time": None,
        }