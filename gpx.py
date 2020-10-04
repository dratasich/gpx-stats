#!/usr/bin/env python3

# %% imports
import argparse
from datetime import datetime
import gpxpy
import logging
import os.path
import pandas as pd
from sqlalchemy import create_engine, exc
import sys

from stats import enrich, summary


# %% parse cli arguments
parser = argparse.ArgumentParser("GPX parser.")
parser.add_argument("gpx", type=argparse.FileType('r'),
                    help="input gpx file")
args = parser.parse_args()

# %% init logger
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] [%(levelname)s] %(message)s")

logging.info(f"Load '{args.gpx.name}'...")

# %% database setup
DB = "gpx.db"
engine = create_engine(f"sqlite:///{DB}")
TABLE_GPX = "gpx"
TABLE_FILES = "files"

# %% check if gpx exists in database
if engine.has_table(TABLE_FILES):
    res = engine.execute(f"""
        SELECT 1 
        FROM {TABLE_FILES}
        WHERE load_path = '{args.gpx.name}'
        """).fetchall()
    if len(res) >= 1:
        logging.error(f"File '{args.gpx.name}' already loaded to database.")
        sys.exit(os.EX_DATAERR)


# %% parse GPX
gpx = gpxpy.parse(args.gpx)
gpxid = gpx.tracks[0].name

# %% check if gpx exists in database
if engine.has_table(TABLE_FILES):
    res = engine.execute(f"""
        SELECT load_path, load_timestamp
        FROM {TABLE_FILES}
        WHERE gpx_name = '{gpxid}'
        """).fetchall()
    if len(res) >= 1:
        logging.error(f"""GPX with same id '{gpxid}' already loaded to database."""
                    f"""Timestamp and path: {res[0][1]} '{res[0]}'""")
        sys.exit(os.EX_DATAERR)


# %% GPX to pandas data frame
data = gpx.tracks[0].segments[0].points
df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time', 'hr', 'acc'])
for segment in gpx.tracks[0].segments:
    for point in segment.points:
        hr = None
        accuracy = None
        for e in point.extensions:
            for i in e:
                if 'hr' in i.tag:
                    hr = int(i.text)
                elif 'accuracy' in i.tag:
                    accuracy = float(i.text)
        df = df.append({'lon': point.longitude, 'lat': point.latitude,
                        'alt': point.elevation, 'time': point.time,
                        'hr': hr, 'acc': accuracy},
                       ignore_index=True)
logging.debug(df)

# %% enrich
df = enrich(df, logging)
stats = summary(df, logging)
logging.info(f"Summary: {stats}")

# %% save gpx data
# gpx identifier
df['gpx_name'] = gpxid
df.to_sql("gpx", engine, if_exists="append")
logging.info(f"GPX data of '{gpxid}' saved to database.")

# %% create meta data
meta = {}
# gpx identifier
meta['gpx_name'] = gpxid
# add some load and file properties for reference
meta['load_timestamp'] = datetime.utcnow().isoformat()
meta['load_path'] = args.gpx.name

# %% save meta data
df = pd.DataFrame.from_records([meta])
df = df.set_index('gpx_name')
df.to_sql("files", engine, if_exists="append")
logging.info(f"GPX meta data of '{gpxid}' saved to database.")
