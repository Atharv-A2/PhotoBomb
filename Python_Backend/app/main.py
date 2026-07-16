from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config.settings import get_settings
from app.core.exceptions.handlers import (
    register_exception_handlers,
)
from app.core.logging.logger import (
    configure_logging,
)
from app.api.v1.auth import router as auth_router
from app.api.v1.media import router as media_router
from app.api.v1.thumbnails import router as thumbnails_router

from app.providers.telegram.lifecycle import (
    TelegramLifecycle,
)
from app.services.cache.media_cache_manager import (
    get_media_cache_manager
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    settings.temp_storage_path.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.thumbnail_storage_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    telegram = TelegramLifecycle.instance()

    #
    # Force creation of the singleton cache manager.
    #
    # This creates cache directories,
    # loads the in-memory index,
    # and performs any startup cleanup.
    #
    cache = get_media_cache_manager()
    cache.initialize()
    await cache.start()

    try:
        telegram.start()
        yield

    finally:
        telegram.shutdown()

        await cache.shutdown()
        cache.cleanup()


configure_logging()

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)


register_exception_handlers(app)


app.include_router(
    auth_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    media_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    thumbnails_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/health/live")
async def live():
    return {"status": "ok"}


@app.get("/health/ready")
async def ready():
    return {"status": "ready"}



from app.api.v1.test_auth import (
    router as test_auth_router,
)
app.include_router(
    test_auth_router
)