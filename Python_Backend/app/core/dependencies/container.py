from functools import lru_cache

from app.core.config.settings import Settings, get_settings


@lru_cache
def get_app_settings() -> Settings:
    return get_settings()