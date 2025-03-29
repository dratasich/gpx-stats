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
    activity: Activity = Activity.UNKNOWN

    def fill_defaults(self):
        if self.distanceMeters != 0 and self.timeSeconds != 0:
            self.speedMetersPerSecond = self.distanceMeters / self.timeSeconds
            distance_km = self.distanceMeters / 1000.0
            min_per_km = int((self.timeSeconds / 60.0) / distance_km)
            sec_remainder = round((self.timeSeconds / distance_km) - (min_per_km * 60))
            self.pace = f"{min_per_km:02d}:{sec_remainder:02d}"
            self.activity = Activity.guess(self.id, self.speedMetersPerSecond)
