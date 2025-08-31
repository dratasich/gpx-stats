import pandas as pd
from stats_loader.parser.gpx import GPXParser
import pytest


@pytest.fixture
def data_dir():
    return "tests/data"


def test_parse_invalid_file(data_dir: str):
    parser = GPXParser()
    # nonexistent file
    with pytest.raises(FileNotFoundError):
        parser.parse(f"{data_dir}/nonexistent.gpx")
    assert parser.filename is None
    assert parser.id is None
    # invalid content
    with pytest.raises(ValueError):
        parser.parse(f"{data_dir}/invalid.gpx")
    assert parser.filename is None
    assert parser.id is None


def test_enrich():
    parser = GPXParser()
    parser._df = pd.DataFrame(
        {
            "lon": [1.0, 2.0],
            "lat": [2.0, 3.0],
            "alt": [3.0, 4.0],
            "time": pd.to_datetime(["2023-01-01T00:00:00Z", "2023-01-01T00:01:00Z"]),
        }
    )
    parser.enrich()
    assert "t" in parser._df.columns
    assert "2d" in parser._df.columns
    assert "delta_t" in parser._df.columns
    assert "delta_2d" in parser._df.columns
    assert "speed" in parser._df.columns


def test_summary():
    parser = GPXParser()
    parser._gpxid = "test"
    parser._df = pd.DataFrame(
        {
            "lon": [1.0, 2.0],
            "lat": [2.0, 3.0],
            "alt": [3.0, 4.0],
            "time": pd.to_datetime(["2023-01-01T00:00:00Z", "2023-01-01T00:01:00Z"]),
            "t": [0, 60],
            "2d": [0, 1000],
            "speed": [0, 3.3],  # will be ignored for stats
        }
    )
    s = parser.summary()
    assert s.distanceMeters == 1000
    assert s.timeSeconds == 60
    assert s.speedMetersPerSecond == 1000 / 60
