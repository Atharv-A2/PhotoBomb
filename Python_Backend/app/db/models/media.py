from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.enums.media_status import MediaStatus
from app.db.enums.media_type import MediaType
from app.db.models.base import Base
from app.db.models.mixins import TimestampMixin
from app.db.models.mixins import UUIDPrimaryKeyMixin
from uuid import UUID, uuid4


class Media(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "media"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )

    media_type: Mapped[MediaType] = mapped_column(
        Enum(MediaType),
        nullable=False,
    )

    status: Mapped[MediaStatus] = mapped_column(
        Enum(MediaStatus),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    temp_path: Mapped[str | None] = mapped_column(
        String(1024)
    )

    width: Mapped[int | None]
    height: Mapped[int | None]

    duration: Mapped[float | None]

    capture_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )