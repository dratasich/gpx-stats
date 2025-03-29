from enum import StrEnum


class Activity(StrEnum):
    """Activity type."""

    Running = "Running"
    Cycling = "Cycling"
    Unknown = "Unknown"

    @staticmethod
    def guess(name: str | None, speed_meters_per_second: float | None) -> "Activity":
        if name is not None:
            if "Running" in name:
                return Activity.Running
            elif "Biking" in name or "Cycling" in name:
                return Activity.Cycling
        if speed_meters_per_second is not None:
            if speed_meters_per_second * 3.6 >= 14:
                return Activity.Cycling
            elif speed_meters_per_second * 3.6 >= 8:
                return Activity.Running
        return Activity.Unknown
