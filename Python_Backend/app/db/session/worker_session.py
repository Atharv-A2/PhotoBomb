from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config.settings import (
    get_settings,
)

settings = get_settings()

sync_database_url = (
    settings.database_url
    .replace(
        "+asyncpg",
        "+psycopg",
    )
)

engine = create_engine(
    sync_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    pool_reset_on_return="rollback"
)
WorkerSessionLocal = (

    sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
)