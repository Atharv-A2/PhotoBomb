from functools import lru_cache

from app.db.enums.storage_provider_type import (
    StorageProviderType,
)

from app.providers.telegram.provider import (
    TelegramProvider,
)

from app.services.storage.base import (
    StorageProvider,
)


class StorageProviderFactory:

    @staticmethod
    @lru_cache(maxsize=None)
    def get(
        provider_type: StorageProviderType,
    ) -> StorageProvider:
        """
        Returns exactly one provider instance per process.

        Providers are thread-safe and own no lifecycle.
        """

        if (
            provider_type
            == StorageProviderType.TELEGRAM
        ):
            return TelegramProvider()

        raise ValueError(
            f"Unsupported storage provider: "
            f"{provider_type}"
        )