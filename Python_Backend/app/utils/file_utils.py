from pathlib import Path
from uuid import uuid4


def build_temp_path(
    root: Path,
    extension: str,
) -> Path:
    return root / (
        f"{uuid4()}{extension}"
    )