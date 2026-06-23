from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "PhotoBomb"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    host: str = "127.0.0.1"
    port: int = 8000

    database_url: str
    redis_url: str

    jwt_secret: str = Field(default="")
    jwt_refresh_secret: str = Field(default="")

    telegram_bot_token: str = Field(default="")
    telegram_media_chat_id: str = Field(default="")

    telegram_api_base: str = ( "https://api.telegram.org" )

    temp_storage_path: Path = (
        BASE_DIR / "storage" / "temp"
    )
    thumbnail_storage_path: Path = (
        BASE_DIR / "storage" / "thumbnails"
    )

    log_level: str = "INFO"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    exiftool_binary: str = "exiftool"


@lru_cache
def get_settings() -> Settings:
    return Settings()