from stats_loader.parser.activity import Activity
from stats_loader.parser.gpx import GPXParser
import pytest


@pytest.fixture
def data_dir():
    return "tests/data"


def test_parse_valid_file(data_dir: str):
    parser = GPXParser()
    parser.parse(f"{data_dir}/RunnerUp_2025-02-03-08-31-00_Running.gpx")
    assert parser.id == "RunnerUp-Running-2025-02-03T07:31:00Z"
    assert parser.filename == "RunnerUp_2025-02-03-08-31-00_Running.gpx"


def test_route_data_no_segments(data_dir: str):
    parser = GPXParser()
    parser.parse(f"{data_dir}/RunnerUp_2025-02-11-17-30-00_Cycling.gpx")
    with pytest.raises(ValueError):
        parser.route_data()


def test_route(data_dir: str):
    parser = GPXParser()
    parser.parse(f"{data_dir}/RunnerUp_2025-02-03-08-31-00_Running.gpx")
    points_df = parser.route_data()
    assert len(points_df) == 1533


def test_implicit_calls_of_summary():
    parser = GPXParser()
    parser.parse("tests/data/RunnerUp_2025-02-03-08-31-00_Running.gpx")
    s = parser.summary()
    assert s.activity == Activity.RUNNING


def test_locations():
    parser = GPXParser()
    parser.parse("tests/data/RunnerUp_2025-02-03-08-31-00_Running.gpx")
    df = parser.locations()
    assert len(df) > 0
    assert "lat" in df.columns
    assert "lon" in df.columns
    assert "id" in df.columns
    assert "activity" in df.columns
    assert "time" in df.reset_index().columns
