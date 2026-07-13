from __future__ import annotations

from telethon.tl.custom.message import Message


class TelegramStream:

    #
    # 1MB chunks generally give much better throughput
    # than 64KB while keeping memory usage low.
    #
    CHUNK_SIZE = 1024 * 1024

    @staticmethod
    async def stream(
        client,
        message: Message,
        start: int,
        end: int,
        chunk_size: int = CHUNK_SIZE,
    ):
        """
        Stream a byte range directly from Telegram.

        Parameters
        ----------
        client
            Telethon client.

        message
            Telegram message containing the media.

        start
            First byte (inclusive)

        end
            Last byte (inclusive)
        """

        media = message.media

        if media is None:
            raise RuntimeError(
                "Telegram message has no media."
            )

        #
        # Telegram iter_download() uses:
        #
        # offset = starting byte
        #
        # limit = total bytes to read
        #
        total = end - start + 1

        downloaded = 0

        async for chunk in client.iter_download(

            media,

            offset=start,

            request_size=chunk_size,

        ):

            if downloaded >= total:
                break

            remaining = total - downloaded

            #
            # Last chunk may extend past
            # the requested range.
            #
            if len(chunk) > remaining:

                chunk = chunk[:remaining]

            downloaded += len(chunk)

            yield chunk



class TelegramRange:

    @staticmethod
    def parse_range(
        header: str | None,
        file_size: int,
    ):

        if not header:
            return (
                0,
                file_size - 1,
            )

        units, value = header.split("=")

        if units != "bytes":
            raise ValueError(
                "Invalid Range header"
            )

        start_str, end_str = value.split("-")

        #
        # bytes=500-
        #
        if start_str:

            start = int(start_str)

        else:

            start = 0

        #
        # bytes=0-499
        #
        if end_str:

            end = int(end_str)

        else:

            end = file_size - 1

        end = min(
            end,
            file_size - 1,
        )

        if start > end:
            raise ValueError(
                "Invalid range"
            )

        return (
            start,
            end,
        )