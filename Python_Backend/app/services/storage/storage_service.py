from pathlib import Path

from app.db.enums.storage_provider_type import (
    StorageProviderType,
)

from app.services.cache.media_cache_manager import (
    get_media_cache_manager
)

from app.services.storage.provider_registry import (
    StorageProviderRegistry,
)

from app.db.models.media_storage import MediaStorage

class StorageService:

    def __init__(self):

        self.provider = (
            StorageProviderRegistry.get(
                StorageProviderType.TELEGRAM
            )
        )
        self.cache = get_media_cache_manager()

    def upload_file(
        self,
        path: Path,
        media_type,
    ):
        return self.provider.upload_file(
            path,
            media_type,
        )

    def download_to_path(
        self,
        storage_metadata,
        destination: Path,
    ):
        return self.provider.download_to_path(
            storage_metadata,
            destination,
        )

    def delete_file(
        self,
        storage_metadata,
    ):
        self.provider.delete_file(
            storage_metadata,
        )

    def download_file(
        self,
        storage_metadata,
    ):

        return self.provider.download_file(
            storage_metadata
        )