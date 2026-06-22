from typing import Annotated

from fastapi import Depends

from app.services.storage.base import (
    StorageProvider,
)
from app.services.storage.factory import (
    get_storage_provider,
)

StorageProviderDep = Annotated[
    StorageProvider,
    Depends(get_storage_provider),
]