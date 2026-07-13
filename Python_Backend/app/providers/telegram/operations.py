from __future__ import annotations

import logging

from pathlib import Path
from typing import AsyncGenerator

from telethon.errors import (
    AuthKeyError,
    FloodWaitError,
    RPCError,
)
from telethon.tl.custom import Message
from telethon.tl.types import Document

from app.providers.telegram.exceptions import (
    TelegramAuthenticationError,
    TelegramConnectionError,
    TelegramDownloadError,
    TelegramMediaNotFoundError,
    TelegramTransportError,
    TelegramUploadError,
)

from app.providers.telegram.models import (
    TelegramMedia,
    TelegramRange,
)

from app.providers.telegram.worker import (
    TelegramWorker,
)

logger = logging.getLogger(__name__)


class TelegramOperations:

    def __init__(
        self,
        worker: TelegramWorker,
    ):

        self._worker = worker


    def _map_exception(
        self,
        exc: Exception,
    ) -> Exception:

        if isinstance(
            exc,
            AuthKeyError,
        ):
            return TelegramAuthenticationError(
                "Telegram authentication failed.",
                cause=exc,
            )

        if isinstance(
            exc,
            FloodWaitError,
        ):
            return TelegramTransportError(
                f"Flood wait: {exc.seconds}s",
                cause=exc,
            )

        if isinstance(
            exc,
            RPCError,
        ):
            return TelegramConnectionError(
                str(exc),
                cause=exc,
            )

        return TelegramTransportError(
            str(exc),
            cause=exc,
        )
    

    async def _resolve_message(
        self,
        media: TelegramMedia,
    ) -> Message:

        message = await (
            self._worker.get_cached_message(
                media.chat_id,
                media.message_id,
            )
        )

        if message is not None:
            return message

        entity = await (
            self._worker.get_entity(
                media.chat_id,
            )
        )

        message = await (
            self._worker.client.get_messages(
                entity,
                ids=media.message_id,
            )
        )

        if message is None:

            raise TelegramMediaNotFoundError(
                f"Telegram message "
                f"{media.message_id} "
                f"not found."
            )

        await self._worker.cache_message(
            message
        )

        return message
    

    async def upload_document(
        self,
        chat_id: int,
        path: Path,
    ) -> TelegramMedia:

        await self._worker.ensure_connected()

        try:

            entity = await (
                self._worker.get_entity(
                    chat_id,
                )
            )

            message = await (
                self._worker.client.send_file(
                    entity,
                    file=str(path),
                    force_document=True,
                )
            )

            await self._worker.cache_message(
                message
            )

            document: Document | None = (
                message.document
            )

            if document is None:

                raise TelegramUploadError(
                    "Uploaded message "
                    "contains no document."
                )

            return TelegramMedia(

                chat_id=int(message.chat_id),

                message_id=int(message.id),

                file_size=document.size,

                mime_type=document.mime_type,

                filename=(
                    document.attributes[0].file_name
                    if (
                        document.attributes
                        and hasattr(
                            document.attributes[0],
                            "file_name",
                        )
                    )
                    else path.name
                ),
            )

        except Exception as exc:

            raise self._map_exception(
                exc
            ) from exc
        

    async def download_to_path(
        self,
        media: TelegramMedia,
        destination: Path,
    ) -> Path:

        await self._worker.ensure_connected()

        try:

            message = await self._resolve_message(
                media
            )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            logger.info(
                "Downloading Telegram message %s -> %s",
                media.message_id,
                destination,
            )

            result = await self._worker.client.download_media(
                message,
                file=str(destination),
            )

            if result is None:

                raise TelegramDownloadError(
                    "Telegram download returned None."
                )

            return destination

        except Exception as exc:

            raise self._map_exception(
                exc
            ) from exc
        

    async def delete(
        self,
        media: TelegramMedia,
    ) -> None:

        await self._worker.ensure_connected()

        try:

            entity = await self._worker.get_entity(
                media.chat_id,
            )

            await self._worker.client.delete_messages(
                entity,
                message_ids=media.message_id,
            )

            self._worker.invalidate_message(
                media.chat_id,
                media.message_id,
            )

        except Exception as exc:

            raise self._map_exception(
                exc
            ) from exc
        

    async def open_stream(
        self,
        media: TelegramMedia,
        byte_range: TelegramRange,
    ) -> AsyncGenerator[
        bytes,
        None,
    ]:

        await self._worker.ensure_connected()

        message = await self._resolve_message(
            media
        )

        logger.info(

            "Opening Telegram stream "
            "message=%s "
            "range=%s-%s",

            media.message_id,

            byte_range.start,

            byte_range.end,
        )

        remaining = byte_range.length
        
        try:

            async for chunk in (
                self._worker.client.iter_download(

                    message,

                    offset=byte_range.start,

                    request_size=1024 * 1024,
                )
            ):

                if remaining <= 0:
                    break

                if len(chunk) > remaining:

                    yield chunk[:remaining]

                    break

                yield chunk

                remaining -= len(chunk)

        except Exception as exc:

            raise self._map_exception(
                exc
            ) from exc
        

    