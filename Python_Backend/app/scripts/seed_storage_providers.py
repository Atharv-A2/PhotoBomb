import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.append(
    str(
        Path(__file__)
        .resolve()
        .parents[2]
    )
)

from app.core.config.settings import (
    get_settings,
)
from app.db.enums.storage_provider_type import (
    StorageProviderType,
)
from app.db.models.storage_provider import (
    StorageProvider,
)

settings = get_settings()

engine = create_engine(
    settings.database_url.replace(
        "+asyncpg",
        "+psycopg",
    )
)

with Session(engine) as session:

    existing = (
        session.query(
            StorageProvider
        )
        .filter(
            StorageProvider.type
            == StorageProviderType.TELEGRAM
        )
        .first()
    )

    if existing is None:

        provider = (
            StorageProvider(
                name="Telegram Primary",
                type=(
                    StorageProviderType
                    .TELEGRAM
                ),
                is_active=True,
            )
        )

        session.add(
            provider
        )

        session.commit()

        print(
            "Telegram provider created"
        )

    else:
        print(
            "Telegram provider already exists"
        )