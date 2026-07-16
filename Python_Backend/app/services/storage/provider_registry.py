from __future__ import annotations

from app.db.enums.storage_provider_type import (
    StorageProviderType,
)

from app.services.storage.factory import (
    StorageProviderFactory,
)


class StorageProviderRegistry:

    _providers: dict = {}

    @classmethod
    def get(
        cls,
        provider_type: StorageProviderType,
    ):

        provider = cls._providers.get(
            provider_type
        )

        if provider is None:

            provider = StorageProviderFactory.get(
                provider_type
            )

            cls._providers[
                provider_type
            ] = provider

        return provider