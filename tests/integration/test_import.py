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
    db_path = f"{int(datetime.now(UTC).timestamp())}_test.db"
    # load data to db
    subprocess.run(f"./load.sh {data_dir} {db_path}", shell=True)
    assert os.path.exists(db_path)
    db = StatsRepository(db_path)
    assert db.has_file("RunnerUp_2025-02-03-08-31-00_Running.gpx")
    assert not db.has_file("RunnerUp_2025-02-11-17-30-00_Cycling.gpx")
    assert db.has_file("RunnerUp_2025-02-11-17-30-00_Cycling.tcx")
    assert not db.has_file("RunnerUp_2025-02-15-11-00-00_Other.tcx")
    # cleanup
    os.remove(db_path)


def test_extra_location_db(data_dir: str):
    db_name = f"{int(datetime.now(UTC).timestamp())}"
    # load data to db
    subprocess.run(
        "uv run python stats_loader/import.py"
        + f" --db {db_name}.db --db-locations {db_name}_locations.db"
        + f" {data_dir}/RunnerUp_2025-02-03-08-31-00_Running.gpx",
        shell=True,
    )
    assert os.path.exists(f"{db_name}.db")
    assert os.path.exists(f"{db_name}_locations.db")
    # cleanup
    os.remove(f"{db_name}.db")
    os.remove(f"{db_name}_locations.db")
