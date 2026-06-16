from datetime import UTC
from datetime import datetime
from datetime import timedelta

from app.core.config.settings import (
    get_settings,
)
from app.core.security.auth import (
    hash_refresh_token,
)
from app.core.security.hashing import (
    hash_password,
    verify_password,
)
from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.db.models.refresh_token import (
    RefreshToken,
)
from app.db.models.user import User

settings = get_settings()