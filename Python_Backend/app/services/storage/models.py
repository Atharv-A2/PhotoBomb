from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class StorageDownloadResult:
    url: str
    expires_at: str | None


@dataclass(slots=True)
class StorageUploadResult:
    storage_key: str
    metadata: dict[str, Any]