from enum import StrEnum


class Activity(StrEnum):
    """Activity type."""

    RUNNING = "Running"
    CYCLING = "Cycling"
    UNKNOWN = "Unknown"

    @staticmethod
    def guess(
        name: str | None, avg_speed: float | None, max_speed: float | None = None
    ) -> "Activity":
        if name is not None:
            if "Running" in name:
                return Activity.RUNNING
            elif "Biking" in name or "Cycling" in name:
                return Activity.CYCLING
        if max_speed is not None:
            if max_speed * 3.6 >= 20 and max_speed <= 100.0:
                return Activity.CYCLING
        if avg_speed is not None:
            if avg_speed * 3.6 >= 12.5:
                return Activity.CYCLING
            elif avg_speed * 3.6 >= 7:
                return Activity.RUNNING
        return Activity.UNKNOWN
