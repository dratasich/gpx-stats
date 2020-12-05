#!/usr/bin/env python3

import argparse
from contextlib import contextmanager
from crate import client
import logging


# parse cli arguments
parser = argparse.ArgumentParser("Load gpx data and stats to database.")
parser.add_argument("--url", type=str, default="localhost:4200",
                    help="URL to the database.")
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG,
                    format="[%(asctime)s] [%(levelname)s] %(message)s")


@contextmanager
def db(url):
    logging.debug("Connect to database.")
    connection = client.connect("localhost:4200")
    try:
        yield connection
    finally:
        cursor.close()
        connection.close()


with db(args.url) as connection:

    with open("out.json", "r", encoding='utf-8') as f:
        container = connection.get_blob_container("stats")
        #tmp = base64.b64decode(f)
        container.put(f)

    cursor = connection.cursor()
    cursor.execute("""SELECT *""")
