from app.providers.telegram.provider import (
    TelegramStorageProvider,
)
from app.services.storage.base import (
    StorageProvider,
)


def get_storage_provider(
) -> StorageProvider:
    return TelegramStorageProvider()