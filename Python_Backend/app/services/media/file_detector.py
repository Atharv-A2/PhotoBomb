from pathlib import Path

import filetype


class FileDetector:

    @staticmethod
    def detect(
        path: Path,
    ):
        kind = filetype.guess(path)

        if kind is None:
            raise ValueError(
                "Unsupported file type"
            )

        return {
            "mime_type": kind.mime,
            "extension": kind.extension,
        }