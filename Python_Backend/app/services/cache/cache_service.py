from pathlib import Path

from app.services.cache.cache_utils import (
    media_cache_path,
)


class CacheService:

    def get_cached_path(
        self,
        storage_key: str,
        extension: str,
    ) -> Path:

        return media_cache_path(
            storage_key,
            extension,
        )

    def exists(
        self,
        storage_key: str,
        extension: str,
    ) -> bool:

        return self.get_cached_path(
            storage_key,
            extension,
        ).exists()

    def save(
        self,
        storage_key: str,
        extension: str,
        data: bytes,
    ) -> Path:

        path = self.get_cached_path(
            storage_key,
            extension,
        )

        path.write_bytes(data)

        return path