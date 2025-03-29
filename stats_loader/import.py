#!/usr/bin/env python3

# %% imports
import argparse
from datetime import UTC, datetime
import logging
import os.path
import sys

from parser.file import File
from parser.gpx import GPXParser
from parser.tcx import TCXParser
from parser.parser import Parser
from stats_repository import StatsRepository

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
repo = StatsRepository(args.db)

# %% check if file exists in database
if repo.has_file(args.path):
    sys.exit(os.EX_DATAERR)


def tcx_backup() -> Parser:
    path = args.path.replace(".gpx", ".tcx")

    # check if file exists in database
    if repo.has_file(path):
        sys.exit(os.EX_DATAERR)

    # try with tcx
    logging.info("Backup: try TCX")
    logging.info(f"Load '{path}'...")
    parser = TCXParser()
    try:
        parser.parse(path)
    except FileNotFoundError as e:
        logging.error(f"No TCX file found (backup for {args.path}). {e}")
    except ValueError as e:
        logging.warning(e)
        sys.exit(os.EX_DATAERR)

    return parser


# %% parse GPX
parser: Parser = GPXParser()
try:
    parser.parse(args.path)
except ValueError as e:
    logging.warning(e)
    parser = tcx_backup()
# %% check if data with same id exists in database
if parser.id is None:
    logging.error("No GPX/TCX id found (error while parsing?).")
    sys.exit(os.EX_DATAERR)
if repo.has_id(parser.id):
    sys.exit(os.EX_DATAERR)

# %% read route/points and extract the summary / stats from it
try:
    stats = parser.summary()
    logging.debug(stats)
except ValueError as e:
    logging.warning(e)
    parser = tcx_backup()
    stats = parser.summary()

# %% save summary to db
repo.save_summary(stats)

# %% save meta data
assert parser.filename is not None, "With a summary we must also have a filename."
f = File(
    id=stats.id,
    loaded=datetime.now(UTC),
    basename=parser.filename,
)
repo.save_file(f)
