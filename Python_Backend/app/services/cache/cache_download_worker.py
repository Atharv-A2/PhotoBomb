from __future__ import annotations
from typing import TYPE_CHECKING
import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

from app.services.cache.models.cache_download_request import (
    CacheDownloadRequest,
)
if TYPE_CHECKING:
    from app.services.cache.media_cache_manager import (
        MediaCacheManager
    )

class CacheDownloadWorker:

    def __init__(
        self,
        coordinator,
        executor,
        cache: "MediaCacheManager",
    ):

        self._queue = asyncio.Queue()

        self._coordinator = coordinator

        self._executor = executor

        self._task = None

        self._running = False

        self._cache = cache


    async def enqueue(
        self,
        request: CacheDownloadRequest,
    ):
        logger.info(
            "Queued cache download %s",
            request.storage_key,
        )

        await self._queue.put(
            request
        )

    async def start(self):

        if self._task:

            return

        self._running = True

        self._task = asyncio.create_task(

            self._run(),

            name="cache-download-worker",
        )

    async def shutdown(self):

        if self._task is None:

            return

        self._running = False

        self._task.cancel()

        try:

            await self._task

        except asyncio.CancelledError:

            pass

        self._task = None
    

    async def _run(self):

        while self._running:

            try:

                request = await asyncio.wait_for(

                    self._queue.get(),

                    timeout=1,

                )

            except asyncio.TimeoutError:

                continue

            try:

                result = await self._executor.execute(
                    request
                )

                await self._cache.complete_download(result)

                await self._coordinator.complete(
                    request.storage_key
                )

            except Exception:

                await self._coordinator.fail(
                    request.storage_key
                )
                logger.exception(
                    "Background cache download failed: %s",
                    request.storage_key,
                )

            finally:

                self._queue.task_done()