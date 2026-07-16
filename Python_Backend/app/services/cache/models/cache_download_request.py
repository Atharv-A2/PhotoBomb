from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CacheDownloadRequest:

    storage_key: str

    storage_metadata: dict

    file_size: int