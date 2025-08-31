from stats_loader.parser.activity import Activity
from stats_loader.parser.gpx import GPXParser
import pytest


@pytest.fixture
def data_dir():
    return "tests/data"


def test_parse_valid_file(data_dir: str):
    parser = GPXParser()
    parser.parse(f"{data_dir}/gadgetbridge-track-2025-08-29T08_00_40+02_00.gpx")
    assert parser.id == "5"
    assert parser.filename == "gadgetbridge-track-2025-08-29T08_00_40+02_00.gpx"


def test_route(data_dir: str):
    parser = GPXParser()
    parser.parse(f"{data_dir}/gadgetbridge-track-2025-08-29T08_00_40+02_00.gpx")
    points_df = parser.route_data()
    # xmllint --format tests/data/gadgetbridge-track-2025-08-29T08_00_40+02_00.gpx | grep /trkpt | wc -l
    assert len(points_df) == 620


def test_summary(data_dir: str):
    parser = GPXParser()
    parser.parse(f"{data_dir}/gadgetbridge-track-2025-08-29T08_00_40+02_00.gpx")
    s = parser.summary()
    assert s.activity == Activity.CYCLING
    assert round(s.timeSeconds / 60) == 11


def test_locations(data_dir: str):
    parser = GPXParser()
    parser.parse(f"{data_dir}/gadgetbridge-track-2025-08-29T08_00_40+02_00.gpx")
    df = parser.locations()
    assert len(df) > 0
    assert "lat" in df.columns
    assert "lon" in df.columns
    assert "id" in df.columns
    assert "activity" in df.columns
    assert "time" in df.reset_index().columns
