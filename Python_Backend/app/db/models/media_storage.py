from sqlalchemy import ForeignKey
from sqlalchemy import JSONB
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from uuid import UUID, uuid4

from app.db.models.base import Base
from app.db.models.mixins import TimestampMixin
from app.db.models.mixins import UUIDPrimaryKeyMixin


class MediaStorage(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "media_storage"

    media_id: Mapped[UUID] = mapped_column(
        ForeignKey("media.id"),
        nullable=False,
        index=True,
    )

    storage_provider_id: Mapped[UUID] = mapped_column(
        ForeignKey("storage_provider.id"),
        nullable=False,
        index=True,
    )

    storage_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    storage_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )