from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class CacheEntry:
    """
    Represents a completed cached media file.
    """

    path: Path

    size: int

    last_access: float