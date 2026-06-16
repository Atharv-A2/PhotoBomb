from sqlalchemy import Boolean
from sqlalchemy import Enum
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.enums.storage_provider_type import (
    StorageProviderType,
)
from app.db.models.base import Base
from app.db.models.mixins import TimestampMixin
from app.db.models.mixins import UUIDPrimaryKeyMixin


class StorageProvider(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "storage_provider"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    type: Mapped[StorageProviderType] = mapped_column(
        Enum(StorageProviderType),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )