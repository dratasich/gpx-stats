#!/usr/bin/env python3

# %% imports
import logging
import os.path
import pandas as pd
from sqlalchemy import create_engine, inspect, text

from stats_loader.parser.file import File
from stats_loader.parser.summary import Summary

logger = logging.getLogger(__name__)


class StatsRepository:
    def __init__(self, db: str, db_locations: str | None = None):
        self._dbname = db
        self._engine = create_engine(f"sqlite:///{db}")
        self._engine_locations = self._engine
        if db_locations is not None:
            self._engine_locations = create_engine(f"sqlite:///{db_locations}")
        self._insp = inspect(self._engine)
        self._TABLE_SUMMARY = "summary"
        self._TABLE_FILES = "files"
        self._TABLE_LOCATIONS = "locations"

    def has_file(self, filename_or_path: str) -> bool:
        """Check if file has been loaded to the db."""
        basename = os.path.basename(filename_or_path)
        insp = inspect(self._engine)
        if insp.has_table(self._TABLE_FILES):
            with self._engine.connect() as conn:
                res = conn.execute(
                    text(f"""
                    select 1
                    from {self._TABLE_FILES}
                    where basename = '{basename}'
                    """)
                ).fetchall()
                if len(res) >= 1:
                    logging.warning(f"File '{basename}' already loaded to database.")
                    return True
        return False

    def has_id(self, gpxid: str) -> bool:
        """Check if gpx id has been loaded to the db."""
        insp = inspect(self._engine)
        if insp.has_table(self._TABLE_FILES):
            with self._engine.connect() as conn:
                res = conn.execute(
                    text(f"""
                    select loaded, basename
                    from {self._TABLE_FILES}
                    where id = '{gpxid}'
                    """)
                ).fetchall()
                if len(res) >= 1:
                    logging.warning(
                        f"""GPX with same id '{gpxid}' already loaded to database."""
                        f"""Timestamp and path: {res[0][1]} '{res[0]}'"""
                    )
                    return True
        return False

    def save_summary(self, stats: Summary):
        """Appends a row to the summary table."""
        pd.DataFrame(stats.__dict__, index=["id"]).to_sql(
            self._TABLE_SUMMARY, self._engine, if_exists="append", index=False
        )
        logging.info(f"Stats of '{stats.id}' ({stats.activity}) saved to database.")

    def save_file(self, file: File):
        """Appends a row to the files table."""
        df = pd.DataFrame.from_records([file.__dict__], index=["id"])
        df.to_sql(self._TABLE_FILES, self._engine, if_exists="append")
        logging.info(f"File data of '{file.id}' saved to database.")

    def save_location(self, df: pd.DataFrame):
        """Appends locations."""
        cols = ["id", "lat", "lon", "activity"]
        df[cols].to_sql(
            self._TABLE_LOCATIONS,
            self._engine_locations,
            if_exists="append",
            index=True,  # index = time -> save too!
        )
        logging.info(f"{len(df)} locations of '{df['id'].iloc[0]}' saved to database.")

    def __del__(self) -> None:
        self._engine.dispose()
        if self._engine_locations:
            self._engine_locations.dispose()
