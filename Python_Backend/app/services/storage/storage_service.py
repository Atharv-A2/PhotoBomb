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

    # async def stream_file(
    #     self,
    #     storage_key: str,
    #     storage_metadata,
    #     byte_range,
    # ):

    #     # storage_key = storage_metadata[
    #     #     "storage_key"
    #     # ]

    #     async for chunk in self.cache.stream(

    #         storage_key=storage_key,

    #         storage_metadata = storage_metadata,

    #         byte_range=byte_range,
    #     ):

    #         yield chunk
