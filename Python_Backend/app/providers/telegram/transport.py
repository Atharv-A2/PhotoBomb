from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import AsyncGenerator

from app.providers.telegram.models import (
    TelegramMedia,
    TelegramRange,
    TelegramStreamHandle,
)

from app.providers.telegram.operations import (
    TelegramOperations,
)

from app.providers.telegram.worker import (
    TelegramWorker,
)

logger = logging.getLogger(__name__)


class TelegramTransport:

    def __init__(self):

        self._worker = (
            TelegramWorker.instance()
        )

        self._operations = (
            TelegramOperations(
                self._worker
            )
        )


    def start(
        self,
    ) -> None:

        self._worker.start()


    def shutdown(
        self,
    ) -> None:

        self._worker.shutdown()


    def upload(
        self,
        chat_id: int,
        path: Path,
    ) -> TelegramMedia:

        logger.info(
            "Uploading %s",
            path.name,
        )

        return self._worker.submit(

            self._operations.upload_document(

                chat_id,

                path,
            ),
            timeout = self._worker.UPLOAD_TIMEOUT
        )
    

    def download_to_path(
        self,
        media: TelegramMedia,
        destination: Path,
    ) -> Path:

        logger.info(
            "Downloading %s",
            media.message_id,
        )

        return self._worker.submit(

            self._operations.download_to_path(

                media,

                destination,
            )
        )
    
    async def download(
        self,
        media: TelegramMedia,
    ) -> AsyncGenerator[bytes, None]:
        
        logger.info(
            "Opening Download stream %s",
            media.message_id,
        )

        async for chunk in self._consume_generator(
            lambda: self._operations.download(media)
        ):
            yield chunk
    

    def delete(
        self,
        media: TelegramMedia,
    ) -> None:

        logger.info(
            "Deleting %s",
            media.message_id,
        )

        self._worker.submit(

            self._operations.delete(
                media
            )
        )
    

    def read_stream(
        self,
        handle: TelegramStreamHandle,
    ) -> bytes | None:

        return self._worker.read_stream(
            handle
        )
    

    def close_stream(
        self,
        handle: TelegramStreamHandle,
    ) -> None:

        self._worker.close_stream(
            handle
        )


    def stream_exists(
        self,
        handle: TelegramStreamHandle,
    ) -> bool:

        return self._worker.stream_exists(
            handle
        )
    

    async def stream(
        self,
        media: TelegramMedia,
        byte_range: TelegramRange,
    ) -> AsyncGenerator[bytes, None]:
        
        logger.info(
            "Opening stream %s",
            media.message_id,
        )
        
        async for chunk in self._consume_generator(
            lambda: self._operations.open_stream(media, byte_range)
        ):
            yield chunk


    async def _await_sync(
        self,
        func,
        *args,
    ):
        """
        Execute a synchronous transport operation without
        blocking the FastAPI event loop.
        """
        return await asyncio.to_thread(
            func,
            *args,
        )
    

    async def _consume_generator(self, factory):

        handle = await self._await_sync(
            self._worker.submit_generator,
            factory,
        )

        try:
            while True:
                chunk = await self._await_sync(
                    self.read_stream,
                    handle,
                )

                if chunk is None:
                    break

                yield chunk

        finally:
            await self._await_sync(
                self.close_stream,
                handle,
            )