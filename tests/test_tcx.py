import pytest

from stats_loader.parser.activity import Activity
from stats_loader.parser.tcx import TCXParser


@pytest.fixture
def data_dir():
    return "tests/data"


def test_parse_valid_file(data_dir: str):
    parser = TCXParser()
    parser.parse(f"{data_dir}/RunnerUp_2025-02-11-17-30-00_Cycling.tcx")
    assert parser.id == "2025-02-11T16:30:00Z"
    assert parser.filename == "RunnerUp_2025-02-11-17-30-00_Cycling.tcx"


def test_parse_invalid_file(data_dir: str):
    parser = TCXParser()
    # nonexistent file
    with pytest.raises(FileNotFoundError):
        parser.parse(f"{data_dir}/nonexistent.tcx")
    assert parser.filename is None
    assert parser.id is None
    # invalid content
    with pytest.raises(ValueError):
        parser.parse(f"{data_dir}/invalid.tcx")
    assert parser.filename is None
    assert parser.id is None


def test_summary(data_dir: str):
    parser = TCXParser()
    parser.parse(f"{data_dir}/RunnerUp_2025-02-11-17-30-00_Cycling.tcx")
    s = parser.summary()
    assert s.activity == Activity.CYCLING
    assert s.timeSeconds == 1620
    assert s.distanceMeters == 7200.0
