#!/usr/bin/env python3

# code derived from
# https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d

import argparse
import gpxpy
import haversine
import logging
import pandas as pd
import math


# parse cli arguments
parser = argparse.ArgumentParser("Generate gpx-stats.")
parser.add_argument("gpx", type=argparse.FileType('r'))
args = parser.parse_args()

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] [%(levelname)s] %(message)s")

# parse GPX
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

try:
    df['time'] = df['time'].dt.tz_localize(None)
    logging.debug("> convert time to seconds for calculations")
    df['timestamp'] = df.apply(lambda row: row['time'].timestamp(), axis=1)
except:
    df['timestamp'] = df.index
logging.debug(df.head())

logging.debug("> time as index")
df = df.set_index('time')

logging.debug("> data including null values")
df_null = df[df.isnull().any(axis=1)]
logging.debug(df_null.head())

logging.debug("> sort by time")
df = df.sort_index()
logging.debug(df.head())
logging.debug(":")
logging.debug(df.tail())

logging.debug("> calculate distance")
df['delta_t'] = (df.timestamp - df.timestamp.shift()).fillna(0)
df['t'] = df['delta_t'].cumsum()
hav2d = [0.0]
hav3d = [0.0]
for i in range(len(df)):
    if i == 0:
        continue
    a = (df.iloc[i-1].lat, df.iloc[i-1].lon)
    b = (df.iloc[i].lat, df.iloc[i].lon)
    hav2d.append(haversine.haversine(a, b, unit=haversine.Unit.METERS))
    dalt = df.iloc[i].alt - df.iloc[i-1].alt
    hav3d.append(math.sqrt(hav2d[-1]**2 + dalt**2))
df['delta_2d'] = hav2d
df['delta_3d'] = hav3d
df['2d'] = df['delta_2d'].cumsum()
df['3d'] = df['delta_3d'].cumsum()
logging.debug(df)

logging.debug(f"distance: {df.iloc[-1]['2d']}")
logging.debug(f"avg km/h: {df.iloc[-1]['2d'] / df.iloc[-1]['t'] * 3.6}")
min_per_km = int(float(df.iloc[-1]['t']) / 60)
sec_remainder = int(float(df.iloc[-1]['t']) - (min_per_km * 60))
logging.debug(f"pace min/km: { float(df.iloc[-1]['t']) / 60.0 / (df.iloc[-1]['2d'] / 1000)}")

logging.info(f"Generated stats from '{args.gpx.name}'.")
