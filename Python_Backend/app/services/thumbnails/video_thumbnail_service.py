import subprocess
from pathlib import Path

from app.core.config.settings import (
    get_settings,
)

settings = get_settings()


class VideoThumbnailService:

    def generate(
        self,
        source: Path,
        destination: Path,
    ):
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = [
            settings.ffmpeg_binary,
            "-i",
            str(source),
            "-ss",
            "00:00:01",
            "-vframes",
            "1",
            "-vf",
            "scale=512:-1",
            "-y",
            str(destination),
        ]

        subprocess.run(
            command,
            check=True,
            capture_output=True,
        )

        return destination