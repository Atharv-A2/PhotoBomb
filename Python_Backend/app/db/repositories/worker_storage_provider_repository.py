from sqlalchemy import select

from app.db.models.storage_provider import (
    StorageProvider,
)
from app.db.enums.storage_provider_type import (
    StorageProviderType,
)


class WorkerStorageProviderRepository:

    def __init__(
        self,
        session,
    ):
        self.session = session

    def get_active(
        self,
        provider_type: StorageProviderType,
    ):
        stmt = (
            select(StorageProvider)
            .where(
                StorageProvider.type
                == provider_type,
                StorageProvider.is_active
                == True,
            )
        )

        result = self.session.execute(
            stmt
        )

        return (
            result.scalar_one_or_none()
        )