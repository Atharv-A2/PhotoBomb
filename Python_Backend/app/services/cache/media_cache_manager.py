from __future__ import annotations

import hashlib
import os
import tempfile
import time, json
from pathlib import Path
import logging
from dataclasses import dataclass
from typing import AsyncGenerator, Callable, Awaitable
import contextlib

from app.core.config.settings import get_settings

from .cache_entry import CacheEntry

settings = get_settings()

logger = logging.getLogger(__name__)


class CacheFilesystem:
    """
    Owns every filesystem operation for the media cache.

    Responsibilities

    - directory creation
    - cache path generation
    - temp file creation
    - promotion
    - deletion
    - stat
    - touch
    - directory enumeration

    No cache policy exists here.
    """

    def __init__(self) -> None:

        self.video_dir = Path(
            settings.VIDEO_CACHE_DIRECTORY
        )

        self.temp_dir = Path(
            settings.VIDEO_CACHE_TEMP_DIRECTORY
        )

    # ----------------------------------------------------------
    # Initialization
    # ----------------------------------------------------------

    def initialize(self) -> None:

        self.video_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.temp_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def cleanup_temp(self) -> None:

        if not self.temp_dir.exists():
            return

        for file in self.temp_dir.iterdir():

            if (
                file.is_file()
                and file.suffix == ".tmp"
            ):

                try:

                    file.unlink()

                except OSError:

                    pass

    # ----------------------------------------------------------
    # Naming
    # ----------------------------------------------------------

    def cache_filename(
        self,
        storage_key: str,
    ) -> str:

        return hashlib.sha256(

            storage_key.encode("utf-8")

        ).hexdigest()

    def cache_path(
        self,
        storage_key: str,
    ) -> Path:

        return (

            self.video_dir

            / self.cache_filename(
                storage_key
            )

        )

    # ----------------------------------------------------------
    # Temporary files
    # ----------------------------------------------------------

    def create_temp(
        self,
    ) -> Path:

        fd, path = tempfile.mkstemp(

            suffix=".tmp",

            dir=self.temp_dir,
        )

        os.close(fd)

        return Path(path)

    # ----------------------------------------------------------
    # Queries
    # ----------------------------------------------------------

    def exists(
        self,
        storage_key: str,
    ) -> bool:

        return self.cache_path(
            storage_key
        ).exists()

    def stat(
        self,
        storage_key: str,
    ):

        return self.cache_path(
            storage_key
        ).stat()

    def touch(
        self,
        storage_key: str,
    ) -> None:

        path = self.cache_path(
            storage_key
        )

        if not path.exists():
            return

        now = time.time()

        os.utime(

            path,

            (now, now),

        )

    # ----------------------------------------------------------
    # Promotion
    # ----------------------------------------------------------

    def promote(
        self,
        temp_path: Path,
        storage_key: str,
    ) -> Path:

        destination = self.cache_path(
            storage_key
        )

        with temp_path.open("rb+") as file:

            file.flush()

            os.fsync(
                file.fileno()
            )

        temp_path.replace(
            destination
        )

        return destination

    # ----------------------------------------------------------
    # Removal
    # ----------------------------------------------------------

    def delete(
        self,
        storage_key: str,
    ) -> None:

        path = self.cache_path(
            storage_key
        )

        if not path.exists():
            return

        try:

            path.unlink()

        except OSError:

            pass

    def delete_temp(
        self,
        temp_path: Path,
    ) -> None:

        if not temp_path.exists():
            return

        try:

            temp_path.unlink()

        except OSError:

            pass

    # ----------------------------------------------------------
    # Enumeration
    # ----------------------------------------------------------

    def list_cache(
        self,
    ) -> list[Path]:

        if not self.video_dir.exists():

            return []

        return [

            file

            for file

            in self.video_dir.iterdir()

            if file.is_file()

        ]

    def total_size(
        self,
    ) -> int:

        total = 0

        for file in self.list_cache():

            try:

                total += (
                    file.stat().st_size
                )

            except OSError:

                continue

        return total
    

class CacheIndex:
    """
    In-memory index of the completed video cache.

    The filesystem is scanned exactly once during startup.

    After initialization every cache lookup is O(1).

    Responsibilities

    - cache lookup
    - cache insertion
    - cache removal
    - last-access tracking
    - current cache size
    - LRU ordering

    This class never performs filesystem operations.
    """

    def __init__(
        self,
        filesystem: CacheFilesystem,
    ) -> None:

        self._filesystem = filesystem

        self._entries: dict[
            str,
            CacheEntry,
        ] = {}

        self._current_size = 0

        self._index_file = (
            filesystem.video_dir
            / "index.json"
        )

        self._dirty = False

        self._TOUCH_INTERVAL = 30.0

    # ----------------------------------------------------------
    # Initialization
    # ----------------------------------------------------------

    def load(self) -> None:
        """
        Load the cache index.

        Preference order:

        1. Load persisted index.json
        2. Fallback to filesystem scan
        """

        self._entries.clear()

        self._current_size = 0

        #
        # Try loading persisted index.
        #
        if self._load_index():
            return

        #
        # No valid index found.
        #
        self._load_from_filesystem()

        #
        # Persist the rebuilt index.
        #
        self._dirty = True

        self.flush()

    def _load_index(self) -> bool:
        """
        Load cache metadata from index.json.

        Returns True if successful.
        Returns False if the index does not exist
        or is invalid.
        """

        if not self._index_file.exists():
            return False

        try:

            with self._index_file.open(
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(f)

        except Exception:

            return False

        if data.get("version") != 1:
            return False

        entries = data.get("entries", {})

        self._entries.clear()

        self._current_size = 0

        repaired = False

        for key, item in entries.items():

            path = Path(item["path"])

            #
            # Skip missing files.
            #
            if not path.exists():

                repaired = True

                continue

            entry = CacheEntry(

                path=path,

                size=item["size"],

                last_access=item["last_access"],
            )

            self._entries[key] = entry

            self._current_size += entry.size

        #
        # If we repaired anything,
        # save the cleaned index.
        #
        if repaired:

            self._dirty = True

            self.flush()

        return True
    

    def _load_from_filesystem(self) -> None:
        """
        Rebuild the cache index by scanning the cache directory.
        """

        self._entries.clear()
        self._current_size = 0

        now = time.time()

        for path in self._filesystem.list_cache():

            # Ignore the persisted metadata file
            if path.name == "index.json":
                continue

            try:
                stat = path.stat()
            except OSError:
                continue

            entry = CacheEntry(
                path=path,
                size=stat.st_size,
                last_access=stat.st_mtime,  # or now
            )

            # The filename is the hashed storage key
            key = path.name

            self._entries[key] = entry
            self._current_size += entry.size
        
        
    def _save_index(self) -> None:
        """
        Write cache metadata atomically.
        """

        data = {

            "version": 1,

            "entries": {

                key: {

                    "path": str(entry.path),

                    "size": entry.size,

                    "last_access": entry.last_access,

                }

                for key, entry
                in self._entries.items()

            },

        }

        temp = self._index_file.with_suffix(
            ".tmp"
        )

        with temp.open(
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(

                data,

                f,

                indent=2,
            )

        temp.replace(
            self._index_file
        )

    # ----------------------------------------------------------
    # Queries
    # ----------------------------------------------------------

    def lookup(
        self,
        storage_key: str,
    ) -> CacheEntry | None:

        key = self._filesystem.cache_filename(
            storage_key
        )

        entry = self._entries.get(key)

        if entry is None:
            return None
        
        self._touch_entry(key, entry)

        return self._entries[key]

    def contains(
        self,
        storage_key: str,
    ) -> bool:

        return self.lookup(
            storage_key
        ) is not None

    def current_size(
        self,
    ) -> int:

        return self._current_size

    def count(
        self,
    ) -> int:

        return len(
            self._entries
        )

    # ----------------------------------------------------------
    # Modification
    # ----------------------------------------------------------

    def insert(
        self,
        storage_key: str,
        path: Path,
    ) -> CacheEntry:

        stat = path.stat()

        key = self._filesystem.cache_filename(
            storage_key
        )

        entry = CacheEntry(

            path=path,

            size=stat.st_size,

            last_access=stat.st_atime,
        )

        previous = self._entries.get(key)

        if previous is not None:

            self._current_size -= previous.size

        self._entries[key] = entry

        self._current_size += entry.size

        self._dirty = True

        return entry

    def remove(
        self,
        storage_key: str,
    ) -> None:

        key = self._filesystem.cache_filename(
            storage_key
        )

        self._dirty = True

        self.remove_by_key(key)

    def remove_by_key(
        self,
        key: str,
    ) -> None:

        entry = self._entries.pop(key, None)

        if entry is None:
            return
        
        self._current_size -= entry.size

        self._dirty = True

    # def touch(
    #     self,
    #     storage_key: str,
    # ) -> None:

    #     key = self._filesystem.cache_filename(
    #         storage_key
    #     )

    #     entry = self._entries.get(
    #         key
    #     )

    #     if entry is None:
    #         return

    #     self._entries[key] = CacheEntry(

    #         path=entry.path,

    #         size=entry.size,

    #         last_access=time.time(),
    #     )


    def _touch_entry(
        self,
        key: str,
        entry: CacheEntry,
    ):

        now = time.time()

        #
        # Prevent excessive metadata updates.
        #
        if now - entry.last_access < self._TOUCH_INTERVAL:
            return

        self._entries[key] = CacheEntry(

            path=entry.path,

            size=entry.size,

            last_access=now,
        )

        self._dirty = True

    # ----------------------------------------------------------
    # LRU
    # ----------------------------------------------------------

    def oldest_first(
        self,
    ) -> list[tuple[str, CacheEntry]]:
        """
        Return cache entries ordered by last access.

        Oldest first.
        """

        return sorted(

            self._entries.items(),

            key=lambda pair:
                pair[1].last_access,
        )

    def newest_first(
        self,
    ) -> list[tuple[str, CacheEntry]]:

        return sorted(

            self._entries.items(),

            key=lambda pair:
                pair[1].last_access,

            reverse=True,
        )

    # ----------------------------------------------------------
    # Debug
    # ----------------------------------------------------------

    def entries(
        self,
    ) -> dict[str, CacheEntry]:

        return dict(
            self._entries
        )
    
    def flush(self) -> None:
        """
        Persist the in-memory cache index to disk.

        Does nothing if nothing has changed.
        """

        if not self._dirty:
            return

        self._save_index()

        self._dirty = False
        

from app.services.cache.cache_coordinator import (
    CacheCoordinator,
)

from app.services.cache.cache_download_worker import (
    CacheDownloadWorker,
)

from app.services.cache.cache_download_executor import (
    CacheDownloadExecutor
)

from app.services.storage.provider_registry import (
    StorageProviderRegistry,
)

from app.services.cache.models.cache_download_request import (
    CacheDownloadRequest,
)

from app.services.cache.models.cache_download_result import (
    CacheDownloadResult,
)

from app.db.enums.storage_provider_type import (
    StorageProviderType,
)

from app.services.cache.cache_utils import (
    media_cache_path,
)
import asyncio
    

class MediaCacheManager:

    def __init__(self):

        self._filesystem = CacheFilesystem()

        self._index = CacheIndex(
            self._filesystem
        )

        self._max_cache_size = (
            settings.VIDEO_CACHE_LIMIT_GB * 1024**3
        )

        self._coordinator = CacheCoordinator()

        self._provider = StorageProviderRegistry.get(
            StorageProviderType.TELEGRAM
        )

        executor = CacheDownloadExecutor(
            filesystem=self._filesystem,
            provider=self._provider,
        )

        self._worker = CacheDownloadWorker(
            coordinator=self._coordinator,
            executor=executor,
            cache=self
        )

        self._flush_task = None


    @property
    def coordinator(self):

        return self._coordinator


    @property
    def worker(self):

        return self._worker
    

    async def start(self):

        await self._worker.start()

        self._flush_task = asyncio.create_task(

            self._flush_loop()
        )


    async def shutdown(self):

        if self._flush_task:

            self._flush_task.cancel()

            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        self._index.flush()

        await self._worker.shutdown()


    def initialize(self):

        self._filesystem.initialize()

        self._filesystem.cleanup_temp()

        self._index.load()

        self._index.flush()


    def cleanup(self):

        self._index.flush()

        self._filesystem.cleanup_temp()


    def lookup(
        self,
        storage_key: str,
    ) -> CacheEntry | None:

        return self._index.lookup(
            storage_key
        )
    
    async def _flush_loop(self):

        while True:

            await asyncio.sleep(60)

            self._index.flush()
    

    # def touch(
    #     self,
    #     storage_key: str,
    # ):

    #     self._filesystem.touch(
    #         storage_key
    #     )

    #     self._index.touch(
    #         storage_key
    #     )


    def create_temp(self):

        return self._filesystem.create_temp()
    

    def delete_temp(
        self,
        temp_path: Path,
    ):

        self._filesystem.delete_temp(
            temp_path
        )


    def promote(
        self,
        storage_key: str,
        temp_path: Path,
    ):

        destination = self._filesystem.promote(

            temp_path,

            storage_key,
        )

        self._index.insert(

            storage_key,

            destination,
        )


    async def schedule_download(
        self,
        storage_key: str,
        storage_metadata: dict,
        file_size: int,
    ):
        """
        Schedule a background cache download.

        This method never waits for completion.
        """

        #
        # Already cached?
        #
        if self._index.lookup(storage_key) is not None:
            return

        #
        # Already downloading?
        #
        if await self._coordinator.contains(storage_key):
            return

        #
        # Become the owner.
        #
        registered = (
            await self._coordinator.register(
                storage_key
            )
        )

        if not registered:
            return

        await self._worker.enqueue(
            CacheDownloadRequest(
                storage_key=storage_key,
                storage_metadata=storage_metadata,
                file_size=file_size,
            )
        )


    async def complete_download(
        self,
        result: CacheDownloadResult,
    ):
        
        self.promote(

            result.storage_key,

            result.temporary_path,
        )

        try:
            await self.ensure_capacity()

        except Exception:
            logger.exception(
                "Failed to enforce cache capacity"
            )
    

    async def ensure_capacity(self):

        while (

            self._index.current_size()

            > self._max_cache_size

        ):

            removed = False

            for hashed_key, entry in self._index.oldest_first():

                if await self._coordinator.contains(
                    hashed_key
                ):
                    continue

                try:

                    entry.path.unlink()

                except OSError:

                    self._index.remove_by_key(
                        hashed_key
                    )

                    continue

                self._index.remove_by_key(
                    hashed_key
                )

                removed = True

                break

            if not removed:

                break


    async def _stream_from_cache(
        self,
        storage_key: str,
        byte_range,
    ):

        entry = self.lookup(
            storage_key
        )

        if entry is None:
            raise FileNotFoundError(
                storage_key
            )

        # self.touch(
        #     storage_key
        # )

        with entry.path.open("rb") as file:

            file.seek(
                byte_range.start
            )

            remaining = (
                byte_range.length
            )

            while remaining > 0:

                chunk = file.read(

                    min(
                        1024 * 1024,
                        remaining,
                    )
                )

                if not chunk:
                    break

                remaining -= len(chunk)

                yield chunk


    async def _stream_from_provider(
        self,
        storage_metadata,
        byte_range,
    ):
        
        """
        Stream directly from the storage provider.

        This method NEVER modifies the cache.
        It is purely a passthrough to the provider.
        """

        async for chunk in self._provider.stream_file(
            storage_metadata,
            byte_range,
        ):

            yield chunk


    #For Images Cache Path Check
    async def get_ensure_cached_path(
        self,
        storage_key,
        extension,
        storage_metadata,
    ):
        path = media_cache_path(
            storage_key,
            extension
        )

        #If Cache Not Exists
        if not path.exists():
            self._provider.download_to_path(
                storage_metadata,
                path
            )
        return path


    async def stream(
        self,
        *,
        storage_key: str,
        storage_metadata: dict,
        byte_range,
    ):
        """
        Unified cache interface.

        Cache hit:
            stream local file.

        Cache miss:
            stream Telegram while populating cache.
        """

        entry = self._index.lookup(storage_key)

        if entry is not None:

            async for chunk in self._stream_from_cache(

                storage_key,

                byte_range,
            ):

                yield chunk

            return

        await self.schedule_download(
            storage_key=storage_key,
            storage_metadata=storage_metadata,
            file_size=int(storage_metadata["file_size"]),
        )

        async for chunk in self._stream_from_provider(

            storage_metadata,

            byte_range,

        ):

            yield chunk

    
_media_cache_manager: MediaCacheManager | None = None


def get_media_cache_manager() -> MediaCacheManager:

    global _media_cache_manager

    if _media_cache_manager is None:

        _media_cache_manager = MediaCacheManager()

    return _media_cache_manager