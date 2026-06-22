from abc import abstractmethod
from pathlib import Path

from app.services.storage.base import (
    StorageProvider,
)
from app.services.storage.models import (
    StorageDownloadResult,
    StorageUploadResult,
)


class TelegramStorageProvider(
    StorageProvider
):

    @abstractmethod
    async def upload_file(
        self,
        file_path: Path,
        media_type: str,
    ) -> StorageUploadResult:
        raise NotImplementedError

    @abstractmethod
    async def download_file(
        self,
        storage_metadata: dict,
        media_quality: str,
    ) -> StorageDownloadResult:
        raise NotImplementedError

    @abstractmethod
    async def delete_file(
        self,
        storage_metadata: dict,
    ) -> None:
        raise NotImplementedError