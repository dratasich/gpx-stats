from enum import StrEnum


class Activity(StrEnum):
    """Activity type."""

    RUNNING = "Running"
    CYCLING = "Cycling"
    UNKNOWN = "Unknown"

    @staticmethod
    def guess(name: str | None, speed_meters_per_second: float | None) -> "Activity":
        if name is not None:
            if "Running" in name:
                return Activity.RUNNING
            elif "Biking" in name or "Cycling" in name:
                return Activity.CYCLING
        if speed_meters_per_second is not None:
            if speed_meters_per_second * 3.6 >= 14:
                return Activity.CYCLING
            elif speed_meters_per_second * 3.6 >= 8:
                return Activity.RUNNING
        return Activity.UNKNOWN
