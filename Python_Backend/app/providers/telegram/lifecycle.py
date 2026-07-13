from __future__ import annotations

import logging
from threading import Lock

from app.providers.telegram.transport import (
    TelegramTransport,
)

logger = logging.getLogger(__name__)


class TelegramLifecycle:
    """
    Process-wide lifecycle manager.

    Owns exactly one TelegramTransport instance
    per process.
    """

    _instance = None
    _instance_lock = Lock()

    def __init__(self):

        self._lock = Lock()

        self._started = False

        self._transport: TelegramTransport | None = None

    @classmethod
    def instance(cls):

        if cls._instance is None:

            with cls._instance_lock:

                if cls._instance is None:

                    cls._instance = cls()

        return cls._instance

    @property
    def transport(self) -> TelegramTransport:

        return self._transport

    def start(self) -> None:

        with self._lock:

            if self._started:
                return
            
            if self._transport is None:
                self._transport = TelegramTransport()

            logger.info(
                "Starting Telegram lifecycle..."
            )

            self._transport.start()

            self._started = True

            logger.info(
                "Telegram lifecycle started."
            )

    def shutdown(self) -> None:

        with self._lock:

            if not self._started:
                return

            logger.info(
                "Stopping Telegram lifecycle..."
            )

            self._transport.shutdown()

            self._started = False

            logger.info(
                "Telegram lifecycle stopped."
            )