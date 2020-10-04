#!/usr/bin/env python3

# code derived from
# https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d

import haversine
import logging
import pandas as pd
import math


def enrich(df, logging):
    """Adds columns to dataframe from a GPX file.

    - delta_t: time in seconds between GPX points (typically constant)
    - t: time in seconds from the first GPX point (cumulative of delta_t)
    - delta_2d: 2D distance travelled between two consecutive GPX points
    - delta_3d: 3D distance travelled between two consecutive GPX points
    - 2d: cumulative 2D distance travelled
    - 3d: cumulative 3D distance travelled
    - speed: delta_2d / delta_t
    """

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
    df['speed'] = df['delta_2d'] / df['delta_t']
    logging.debug(df)

    return df


def summary(df, logging):
    """Returns some statistics.

    Prerequisite: GPX dataframe is enriched.
    """
    logging.debug(f"distance: {df.iloc[-1]['2d']}")
    logging.debug(f"avg km/h: {df.iloc[-1]['2d'] / df.iloc[-1]['t'] * 3.6}")
    distance_km = df.iloc[-1]['2d'] / 1000.0
    min_per_km = int((df.iloc[-1]['t'] / 60.0) / distance_km)
    sec_remainder = round((df.iloc[-1]['t'] / distance_km) - (min_per_km * 60))
    logging.debug(
        f"pace min/km: { float(df.iloc[-1]['t']) / 60.0 / (df.iloc[-1]['2d'] / 1000)}")
    logging.debug(f"pace min/km: {min_per_km}:{sec_remainder}")

    return {
        "timeSeconds": df.iloc[-1]['t'],
        "distanceMeters": df.iloc[-1]['2d'],
        "speed": {
            "avg": df['speed'].mean(),
            "kilometersPerHour": df.iloc[-1]['2d'] / df.iloc[-1]['t'] * 3.6,
            "pace": f"{min_per_km}:{sec_remainder}"
        },
    }
