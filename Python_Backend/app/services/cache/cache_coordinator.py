from __future__ import annotations

import asyncio

from app.services.cache.models.cache_download_state import (
    CacheDownloadState,
    CacheDownloadStatus,
)


class CacheCoordinator:
    """
    Coordinates background cache downloads.

    Guarantees:

    - exactly one download per storage_key
    - thread-safe registration/removal
    - no duplicate queueing
    """

    def __init__(self):

        self._lock = asyncio.Lock()

        self._downloads: dict[
            str,
            CacheDownloadState,
        ] = {}

    async def register(
        self,
        storage_key: str,
    ) -> bool:
        """
        Returns True if caller becomes the owner.

        False if another download
        already exists.
        """

        async with self._lock:

            if storage_key in self._downloads:
                return False

            self._downloads[
                storage_key
            ] = CacheDownloadState(

                storage_key=storage_key,

                status=CacheDownloadStatus.QUEUED,
            )

            return True

    async def mark_downloading(
        self,
        storage_key: str,
        task: asyncio.Task,
    ):

        async with self._lock:

            state = self._downloads.get(
                storage_key
            )

            if state is None:
                return

            state.future = task

            state.status = (
                CacheDownloadStatus.DOWNLOADING
            )

    async def complete(
        self,
        storage_key: str,
    ):

        async with self._lock:

            self._downloads.pop(
                storage_key,
                None,
            )

    async def fail(
        self,
        storage_key: str,
    ):

        async with self._lock:

            self._downloads.pop(
                storage_key,
                None,
            )

    async def contains(
        self,
        storage_key: str,
    ) -> bool:

        async with self._lock:

            return (
                storage_key
                in self._downloads
            )

    async def count(
        self,
    ) -> int:

        async with self._lock:

            return len(
                self._downloads
            )