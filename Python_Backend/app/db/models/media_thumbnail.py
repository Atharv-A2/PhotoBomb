from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.enums.thumbnail_type import ThumbnailType
from app.db.models.base import Base
from app.db.models.mixins import TimestampMixin
from app.db.models.mixins import UUIDPrimaryKeyMixin
from uuid import UUID, uuid4


class MediaThumbnail(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "media_thumbnail"

    media_id: Mapped[UUID] = mapped_column(
        ForeignKey("media.id"),
        nullable=False,
        index=True,
    )

    thumbnail_type: Mapped[ThumbnailType] = mapped_column(
        Enum(ThumbnailType),
        nullable=False,
    )

    path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    width: Mapped[int] = mapped_column(
        nullable=False
    )

    height: Mapped[int] = mapped_column(
        nullable=False
    )

    size_bytes: Mapped[int] = mapped_column(
        nullable=False
    )