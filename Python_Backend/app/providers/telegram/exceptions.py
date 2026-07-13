from __future__ import annotations


class TelegramError(Exception):
    """
    Base exception for the Telegram transport subsystem.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.cause = cause


class TelegramConnectionError(TelegramError):
    """
    Telegram connection failed.
    """


class TelegramAuthenticationError(TelegramError):
    """
    Telegram authorization/session failed.
    """


class TelegramTimeoutError(TelegramError):
    """
    RPC or stream timeout.
    """


class TelegramMediaNotFoundError(TelegramError):
    """
    Requested Telegram message/media was not found.
    """


class TelegramPermissionError(TelegramError):
    """
    Telegram denied access to the resource.
    """


class TelegramTransportError(TelegramError):
    """
    Unexpected transport-level failure.
    """


class TelegramStreamClosedError(TelegramError):
    """
    Stream has already been closed.
    """


class TelegramWorkerStoppedError(TelegramError):
    """
    Worker is not running.
    """


class TelegramInvalidRangeError(TelegramError):
    """
    Invalid HTTP range request.
    """


class TelegramUploadError(TelegramError):
    """
    Upload failed.
    """


class TelegramDownloadError(TelegramError):
    """
    Download failed.
    """