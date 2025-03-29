from dataclasses import dataclass
from datetime import datetime


@dataclass
class File:
    id: str
    loaded: datetime
    basename: str
