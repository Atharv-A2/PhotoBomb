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

    yield


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