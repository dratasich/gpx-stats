from dataclasses import dataclass
from datetime import datetime

from .activity import Activity


@dataclass
class Summary:
    id: str
    date: datetime
    timeSeconds: int
    distanceMeters: float
    # defaults (added only when distance > 0)
    speedMetersPerSecond: float | None = None
    pace: str | None = None
    activity: Activity = Activity.Unknown
