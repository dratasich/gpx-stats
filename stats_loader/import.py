#!/usr/bin/env python3

# %% imports
import argparse
from datetime import UTC, datetime
import logging
import os.path
import pandas as pd
from sqlalchemy import create_engine, inspect, text
import sys

from parser.file import File
from parser.gpx import GPXParser


# %% parse cli arguments
argparser = argparse.ArgumentParser("Activity summary importer.")
argparser.add_argument("path", type=str, help="path to input file")
argparser.add_argument("--db", type=str, help="path to db", default="db/test.db")
args = argparser.parse_args()

# %% init logger
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s"
)

logging.info(f"Load '{args.path}'...")

# %% database setup
DB = args.db
engine = create_engine(f"sqlite:///{DB}")
TABLE_FILES = "files"

# %% get metadata
insp = inspect(engine)

# %% check if gpx exists in database
if insp.has_table(TABLE_FILES):
    with engine.connect() as conn:
        res = conn.execute(
            text(f"""
            select 1
            from {TABLE_FILES}
            where load_path = '{args.gpx.name}'
            """)
        ).fetchall()
        if len(res) >= 1:
            logging.warning(f"File '{args.gpx.name}' already loaded to database.")
            sys.exit(os.EX_DATAERR)


# %% parse GPX
parser = GPXParser()
parser.parse(args.path)
gpxid = parser.gpxid

# %% check if gpx exists in database
if insp.has_table(TABLE_FILES):
    with engine.connect() as conn:
        res = conn.execute(
            text(f"""
            SELECT load_path, load_timestamp
            FROM {TABLE_FILES}
            WHERE gpx_name = '{gpxid}'
            """)
        ).fetchall()
        if len(res) >= 1:
            logging.error(
                f"""GPX with same id '{gpxid}' already loaded to database."""
                f"""Timestamp and path: {res[0][1]} '{res[0]}'"""
            )
            sys.exit(os.EX_DATAERR)


# %% read route/points and extract the summary / stats from it
stats = parser.summary()
logging.debug(stats)


# %% save summary to db
pd.DataFrame(stats.__dict__, index=["id"]).to_sql(
    "summary", engine, if_exists="append", index=False
)
logging.info(f"GPX stats of '{stats.id}' saved to database.")

# %% create meta data
assert parser.filename is not None, "With a summary we must also have a filename."
f = File(
    id=stats.id,
    loaded=datetime.now(UTC),
    basename=parser.filename,
)

# %% save meta data
df = pd.DataFrame.from_records([f.__dict__], index=["id"])
df.to_sql("files", engine, if_exists="append")
logging.info(f"File data of '{f.id}' saved to database.")
