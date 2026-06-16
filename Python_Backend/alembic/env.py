import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.models.base import Base
from app.db.models import *

target_metadata = Base.metadata