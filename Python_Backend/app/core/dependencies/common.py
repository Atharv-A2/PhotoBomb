from typing import Annotated

from fastapi import Depends

from app.core.config.settings import Settings
from app.core.dependencies.container import get_app_settings

SettingsDep = Annotated[
    Settings,
    Depends(get_app_settings),
]