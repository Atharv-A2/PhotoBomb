from pathlib import Path

from app.core.config.settings import (
    get_settings,
)

settings = get_settings()


def media_cache_root() -> Path:
    root = (
        settings.temp_storage_path.parent
        / "cache"
    )

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    return root


def media_cache_path(
    storage_key: str,
    extension: str,
) -> Path:

    filename = (
        storage_key.replace(
            ":",
            "_",
        )
        + extension
    )

    return (
        media_cache_root()
        / filename
    )