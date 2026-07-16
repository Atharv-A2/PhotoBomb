from __future__ import annotations

from pathlib import Path

from app.services.cache.models.cache_download_request import (
    CacheDownloadRequest,
)
from app.services.cache.models.cache_download_result import (
    CacheDownloadResult,
)


class CacheDownloadExecutor:

    def __init__(
        self,
        filesystem,
        provider,
    ):
        self._filesystem = filesystem

        self._provider = provider

    async def execute(
        self,
        request: CacheDownloadRequest,
    ):

        temp = self._filesystem.create_temp()

        try:

            #
            # download_to_path()
            # will be made async later if necessary.
            #

            self._provider.download_to_path(

                request.storage_metadata,

                temp,
            )

            #
            # Verify complete download.
            #

            actual = temp.stat().st_size

            if actual != request.file_size:

                raise RuntimeError(

                    f"Incomplete cache download "
                    f"{actual}/{request.file_size}"

                )

            return CacheDownloadResult(

                storage_key=request.storage_key,

                temporary_path=temp,

                size=actual,
            )

        except Exception:

            if temp.exists():

                #
                # promote()
                # already renamed it.
                #
                temp.unlink()
            raise