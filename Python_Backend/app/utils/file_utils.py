from pathlib import Path
from uuid import uuid4
import shutil


def build_temp_path(
    root: Path,
    extension: str,
) -> Path:
    return (
        root
        / f"{uuid4()}{extension}"
    )


def move_file(
    source: Path,
    destination: Path,
):
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.move(
        str(source),
        str(destination),
    )