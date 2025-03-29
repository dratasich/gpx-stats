"""Integration test."""

import os
import pytest
import subprocess
from datetime import datetime, UTC

from stats_loader.stats_repository import StatsRepository


@pytest.fixture
def data_dir():
    return "tests/data"


def test_load_script(data_dir: str):
    db_path = f"{datetime.now(UTC).timestamp()}_test.db"
    # load data to db
    subprocess.run(f"./load.sh {data_dir} {db_path}", shell=True, check=True)
    assert os.path.exists(db_path)
    db = StatsRepository(db_path)
    assert db.has_file("RunnerUp_2025-02-03-08-31-00_Running.gpx")
    assert not db.has_file("RunnerUp_2025-02-11-17-30-00_Cycling.gpx")
    assert db.has_file("RunnerUp_2025-02-11-17-30-00_Cycling.tcx")
    assert not db.has_file("RunnerUp_2025-02-15-11-00-00_Other.tcx")
    # cleanup
    os.remove(db_path)
