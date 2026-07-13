from __future__ import annotations

import asyncio
import atexit
import logging
import threading
import time
import uuid

from collections import OrderedDict
from concurrent.futures import Future
from dataclasses import dataclass
from threading import RLock
from threading import Thread
from typing import Any
from typing import AsyncGenerator
from typing import Coroutine
from typing import Generic
from typing import Optional
from typing import TypeVar

from telethon import TelegramClient

from app.core.config.settings import (
    get_settings,
)
from app.providers.telegram.session import (
    create_session,
)
from app.providers.telegram.models import (
    TelegramStreamHandle,
)
from app.providers.telegram.exceptions import (
    TelegramWorkerStoppedError,
)
from app.providers.telegram.exceptions import (
    TelegramAuthenticationError,
)

settings = get_settings()

logger = logging.getLogger(__name__)

T = TypeVar("T")



@dataclass(slots=True)
class WorkerStream:
    """
    Internal stream state.

    Never leaves TelegramWorker.
    """

    stream_id: str

    generator: AsyncGenerator[
        bytes,
        None,
    ]

    bytes_sent: int = 0

    closed: bool = False

    created_at: float = 0.0

    last_access: float = 0.0
    
    reading: bool = False

    closing: bool = False


@dataclass(slots=True)
class WorkerStatistics:

    rpc_calls: int = 0

    active_tasks: int = 0

    active_streams: int = 0

    cache_hits: int = 0

    cache_misses: int = 0




class TelegramWorker:

    RPC_TIMEOUT = 120

    STREAM_IDLE_TIMEOUT = 300

    MESSAGE_CACHE_SIZE = 1000

    THREAD_NAME = "telegram-worker"

    _instance: Optional["TelegramWorker"] = None

    _instance_lock = threading.Lock()


    #Instance
    @classmethod
    def instance(
        cls,
    ) -> "TelegramWorker":

        if cls._instance is None:

            with cls._instance_lock:

                if cls._instance is None:

                    cls._instance = cls()

        return cls._instance
    


    def __init__(self):

        if TelegramWorker._instance is not None:

            raise RuntimeError(
                "Use TelegramWorker.instance()."
            )

        #
        # Runtime
        #
        self._loop: asyncio.AbstractEventLoop | None = None

        self._thread: Thread | None = None

        self._client: TelegramClient | None = None

        self._started = False

        #
        # Synchronization
        #
        self._lock = RLock()

        #
        # Entity Cache
        #
        self._entity_cache: dict[int, Any] = {}

        #
        # Message Cache (LRU)
        #
        self._message_cache: OrderedDict[
            tuple[int, int],
            Any,
        ] = OrderedDict()

        #
        # Active RPC Tasks
        #
        self._tasks: set[Future] = set()

        #
        # Active Streams
        #
        self._streams: dict[
            str,
            WorkerStream,
        ] = {}

        #
        # Statistics
        #
        self._stats = WorkerStatistics()

        atexit.register(
            self.shutdown
        )

    
    @property
    def client(
        self,
    ) -> TelegramClient:

        client = self._client

        if client is None:

            raise TelegramWorkerStoppedError(
                "Telegram client is not initialized."
            )

        return client
    

    @property
    def loop(
        self,
    ) -> asyncio.AbstractEventLoop:

        loop = self._loop

        if loop is None:

            raise TelegramWorkerStoppedError(
                "Telegram event loop is not initialized."
            )

        return loop
    

    @property
    def started(
        self,
    ) -> bool:

        return self._started
    

    @property
    def statistics(
        self,
    ) -> WorkerStatistics:

        self._stats.active_tasks = len(
            self._tasks
        )

        self._stats.active_streams = len(
            self._streams
        )

        return self._stats
        

    def start(
        self,
    ) -> None:

        with self._lock:

            if self._started:
                return

            logger.info(
                "Starting TelegramWorker..."
            )

            self._loop = asyncio.new_event_loop()

            self._thread = Thread(

                target=self._run_loop,

                name=self.THREAD_NAME,

                daemon=True,
            )

            self._thread.start()

            future = asyncio.run_coroutine_threadsafe(

                self._startup(),

                self.loop,
            )

            future.result(
                timeout=self.RPC_TIMEOUT
            )

            self._started = True

            logger.info(
                "TelegramWorker started."
            )


    def _run_loop(
        self,
    ) -> None:

        loop = self.loop

        asyncio.set_event_loop(loop)

        try:

            loop.run_forever()

        finally:

            #
            # Finish pending async generators.
            #
            loop.run_until_complete(
                loop.shutdown_asyncgens()
            )

            #
            # Close the loop from the owning thread.
            #
            loop.close()


    async def _startup(
        self,
    ) -> None:

        logger.info(
            "Initializing Telethon client..."
        )

        self._client = TelegramClient(

            session=create_session(),

            api_id=settings.telegram_api_id,

            api_hash=settings.telegram_api_hash,
        )

        await self._client.start()

        me = await self._client.get_me()

        logger.info(

            "Connected as %s (%s)",

            me.first_name,

            me.id,
        )


    def _submit_future(
        self,
        coroutine: Coroutine[Any, Any, T],
    ) -> Future[T]:
        """
        Schedule a coroutine onto the Telegram event loop.

        This is the ONLY place in the entire project that
        calls asyncio.run_coroutine_threadsafe().
        """

        if not self._started:

            raise TelegramWorkerStoppedError(
                "TelegramWorker is not running."
            )

        future: Future[T] = asyncio.run_coroutine_threadsafe(
            coroutine,
            self.loop,
        )

        self.register_task(
            future
        )

        return future


    def submit(
        self,
        coroutine: Coroutine[Any, Any, T],
        timeout: int | None = None,
    ) -> T:

        future = self._submit_future(
            coroutine
        )

        try:

            result = future.result(
                timeout=timeout
                or self.RPC_TIMEOUT
            )

            self._stats.rpc_calls += 1

            return result

        except Exception:

            future.cancel()

            raise


    def register_task(
        self,
        future: Future,
    ) -> None:

        self._tasks.add(
            future
        )

        self._stats.active_tasks = len(
            self._tasks
        )

        def _cleanup(
            completed: Future,
        ):

            self._tasks.discard(
                completed
            )

            self._stats.active_tasks = len(
                self._tasks
            )

        future.add_done_callback(
            _cleanup
        )


    def active_tasks(
        self,
    ) -> int:

        return len(
            self._tasks
        )
    

    async def ensure_connected(
        self,
    ) -> None:

        if self.client.is_connected():
            return

        logger.warning(
            "Telegram connection lost. Reconnecting..."
        )

        await self.reconnect()


    async def reconnect(
        self,
    ) -> None:

        if self.client.is_connected():
            return

        await self.client.connect()

        if not await self.client.is_user_authorized():

            raise TelegramAuthenticationError(
                "Telegram authorization failed."
            )

        logger.info(
            "Telegram reconnected."
        )


    async def health_check(
        self,
    ) -> bool:

        try:

            await self.ensure_connected()

            me = await self.client.get_me()

            return me is not None

        except Exception:

            logger.exception(
                "Telegram health check failed."
            )

            return False
        

    def _increment_cache_hit(
        self,
    ) -> None:

        self._stats.cache_hits += 1


    def _increment_cache_miss(
        self,
    ) -> None:

        self._stats.cache_misses += 1


    async def get_entity(
        self,
        chat_id: int,
    ) -> Any:

        entity = self._entity_cache.get(
            chat_id
        )

        if entity is not None:

            self._increment_cache_hit()

            return entity

        self._increment_cache_miss()

        await self.ensure_connected()

        logger.debug(
            "Resolving Telegram entity %s",
            chat_id,
        )

        entity = await self.client.get_entity(
            chat_id
        )

        self._entity_cache[
            chat_id
        ] = entity

        return entity
    

    async def cache_message(
        self,
        message: Any,
    ) -> None:

        key = (
            int(message.chat_id),
            int(message.id),
        )

        #
        # Refresh LRU position
        #
        if key in self._message_cache:

            self._message_cache.move_to_end(
                key
            )

            self._message_cache[
                key
            ] = message

            return

        self._message_cache[
            key
        ] = message

        self._evict_message_cache()


    async def get_cached_message(
        self,
        chat_id: int,
        message_id: int,
    ) -> Any | None:

        key = (
            chat_id,
            message_id,
        )

        message = self._message_cache.get(
            key
        )

        if message is None:

            self._increment_cache_miss()

            return None

        #
        # Refresh LRU order
        #
        self._message_cache.move_to_end(
            key
        )

        self._increment_cache_hit()

        return message
    

    def invalidate_message(
        self,
        chat_id: int,
        message_id: int,
    ) -> None:

        self._message_cache.pop(

            (
                chat_id,
                message_id,
            ),

            None,
        )


    def clear_message_cache(
        self,
    ) -> None:

        self._message_cache.clear()

        self._stats.cache_hits = 0

        self._stats.cache_misses = 0


    def clear_entity_cache(
        self,
    ) -> None:

        self._entity_cache.clear()


    def _evict_message_cache(
        self,
    ) -> None:

        while (

            len(self._message_cache)

            > self.MESSAGE_CACHE_SIZE

        ):

            #
            # Remove oldest (LRU)
            #
            self._message_cache.popitem(

                last=False
            )


    def submit_generator(
        self,
        factory,
    ) -> TelegramStreamHandle:
        """
        Creates an async generator inside the
        Telegram event loop.

        The generator never leaves the worker.
        """

        if not self._started:

            raise TelegramWorkerStoppedError(
                "TelegramWorker is not running."
            )

        async def _create():

            generator = factory()

            stream_id = uuid.uuid4().hex

            stream = WorkerStream(

                stream_id=stream_id,

                generator=generator,

                created_at=time.monotonic(),

                last_access=time.monotonic(),
            )

            self._streams[
                stream_id
            ] = stream

            self._stats.active_streams = len(
                self._streams
            )

            return TelegramStreamHandle(
                stream_id=stream_id
            )

        future = self._submit_future(
            _create()
        )

        return future.result(
            timeout=self.RPC_TIMEOUT
        )
            

    def stream_exists(
        self,
        handle: TelegramStreamHandle,
    ) -> bool:

        return (
            handle.stream_id
            in self._streams
        )
    

    def active_streams(
        self,
    ) -> int:

        return len(
            self._streams
        )
        

    def read_stream(
        self,
        handle: TelegramStreamHandle,
    ) -> bytes | None:

        if not self._started:

            raise TelegramWorkerStoppedError(
                "TelegramWorker is not running."
            )

        stream = self._streams.get(
            handle.stream_id
        )

        if stream is None:

            return None

        async def _next():

            try:
                stream.reading = True

                chunk = await (
                    stream.generator.__anext__()
                )

                stream.bytes_sent += len(
                    chunk
                )

                stream.last_access = (
                    time.monotonic()
                )

                stream.reading = False

                return chunk

            except StopAsyncIteration:

                return None

        future = self._submit_future(
            _next()
        )

        chunk = future.result(
            timeout=self.STREAM_IDLE_TIMEOUT
        )

        if chunk is None:

            self.close_stream(
                handle
            )

        return chunk
    

    def close_stream(
        self,
        handle: TelegramStreamHandle,
    ) -> None:

        stream = self._streams.pop(

            handle.stream_id,

            None,
        )

        self._stats.active_streams = len(
            self._streams
        )

        if stream is None:
            return

        if stream.closed:
            return

        stream.closed = True

        if stream.reading:
            stream.closing = True
            return

        async def _close():
            
            if stream.closing:
                await stream.generator.aclose()

        try:

            future = self._submit_future(
                _close()
            )

            future.result(
                timeout=self.RPC_TIMEOUT
            )

        except Exception:

            logger.exception(
                "Failed to close stream %s",
                handle.stream_id,
            )


    def shutdown(
        self,
    ) -> None:

        with self._lock:

            if not self._started:
                return

            logger.info(
                "Shutting down TelegramWorker..."
            )

            #
            # Close all active streams first.
            #
            for stream_id in list(
                self._streams.keys()
            ):

                try:

                    self.close_stream(
                        TelegramStreamHandle(
                            stream_id=stream_id
                        )
                    )

                except Exception:

                    logger.exception(
                        "Failed closing stream %s",
                        stream_id,
                    )

            #
            # Cancel outstanding RPCs.
            #
            for future in list(
                self._tasks
            ):

                if not future.done():

                    future.cancel()

            self._tasks.clear()

            #
            # Disconnect Telethon and stop loop.
            #
            if self._loop is not None:

                future = (
                    asyncio.run_coroutine_threadsafe(

                        self._shutdown_async(),

                        self._loop,
                    )
                )

                try:

                    future.result(
                        timeout=self.RPC_TIMEOUT
                    )

                except Exception:

                    logger.exception(
                        "Telegram shutdown failed."
                    )

                self._loop.call_soon_threadsafe(
                    self._loop.stop
                )

            #
            # Wait for worker thread.
            #
            if self._thread is not None:

                self._thread.join(
                    timeout=10
                )

            #
            # Clear runtime state.
            #
            self.clear_entity_cache()

            self.clear_message_cache()

            self._streams.clear()

            self._client = None

            self._loop = None

            self._thread = None

            self._started = False

            logger.info(
                "TelegramWorker shutdown complete."
            )


    async def _shutdown_async(
        self,
    ) -> None:

        logger.info(
            "Disconnecting Telegram..."
        )

        if self._client is not None:

            try:

                if self._client.is_connected():

                    await self._client.disconnect()

            except Exception:

                logger.exception(
                    "Telethon disconnect failed."
                )

    
