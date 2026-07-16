from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class CacheDownloadResult:

    storage_key: str

    temporary_path: Path

    size: int