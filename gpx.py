#!/usr/bin/env python3

import argparse
import gpxpy
import logging
import pandas as pd

from stats import enrich, summary

# parse cli arguments
parser = argparse.ArgumentParser("GPX parser.")
parser.add_argument("gpx", type=argparse.FileType('r'),
                    help="input gpx file")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] [%(levelname)s] %(message)s")


# %% parse GPX
gpx = gpxpy.parse(args.gpx)
data = gpx.tracks[0].segments[0].points

# GPX to pandas data frame
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
logging.info(stats)
