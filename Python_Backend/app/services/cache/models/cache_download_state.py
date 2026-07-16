from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import asyncio
import time


class CacheDownloadStatus(str, Enum):

    QUEUED = "QUEUED"

    DOWNLOADING = "DOWNLOADING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"


@dataclass(slots=True)
class CacheDownloadState:

    storage_key: str

    status: CacheDownloadStatus

    future: asyncio.Task | None = None

    started_at: float = 0.0

    queued_at: float = time.time()