from datetime import UTC, datetime

from stats_loader.parser.activity import Activity
from stats_loader.parser.summary import Summary


def test_fill_defaults():
    s = Summary(
        id="2025-02-11T16:30:00Z",
        date=datetime(2025, 2, 11, 16, 30, 0, tzinfo=UTC),
        timeSeconds=1620,
        distanceMeters=7200.0,
    )
    s.fill_defaults()
    assert s.activity == Activity.CYCLING
    assert s.pace == "03:45"
    assert s.speedMetersPerSecond == 4.444444444444445
