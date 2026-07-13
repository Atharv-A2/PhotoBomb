from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import Future
from pathlib import Path
from typing import AsyncIterator


@dataclass(slots=True, frozen=True)
class TelegramMedia:

    chat_id: int

    message_id: int

    file_size: int

    mime_type: str | None

    filename: str | None


@dataclass(slots=True)
class TelegramUpload:

    media: TelegramMedia

    storage_key: str


@dataclass(slots=True)
class TelegramDownload:

    media: TelegramMedia

    destination: Path


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramRange:

    start: int

    end: int

    total_size: int

    @property
    def length(
        self,
    ) -> int:

        return (
            self.end
            - self.start
            + 1
        )

    @classmethod
    def from_header(
        cls,
        header: str | None,
        file_size: int,
    ):

        if not header:

            return cls(

                start=0,

                end=file_size - 1,

                total_size=file_size,
            )

        _, value = header.split("=")

        start, end = value.split("-")

        start = int(start)

        end = (
            int(end)
            if end
            else file_size - 1
        )

        if start < 0:

            start = 0

        if end >= file_size:

            end = file_size - 1

        if end < start:

            raise ValueError(
                "Invalid HTTP range."
            )

        return cls(

            start=start,

            end=end,

            total_size=file_size,
        )


@dataclass(slots=True)
class TelegramStream:

    id: str

    media: TelegramMedia

    byte_range: TelegramRange

    iterator: AsyncIterator[bytes]


@dataclass(slots=True)
class TelegramHealth:

    connected: bool

    authorized: bool

    dc_id: int | None


@dataclass(slots=True, frozen=True)
class TelegramStreamHandle:

    stream_id: str