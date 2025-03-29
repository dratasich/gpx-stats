#!/usr/bin/env python3

# %% imports
import logging
import math
import os
import gpxpy
import haversine
import pandas as pd

from .activity import Activity
from .summary import Summary

logger = logging.getLogger(__name__)


class GPXParser:
    def __init__(self):
        # default values
        self._filename: str | None = None
        self._gpxid: str | None = None
        self._df: pd.DataFrame | None = None

    @property
    def filename(self) -> str | None:
        return self._filename

    @property
    def gpxid(self) -> str | None:
        return self._gpxid

    def parse(self, filename):
        """Parse gpx file."""
        with open(filename, "r") as f:
            self._gpx = gpxpy.parse(f)
        if len(self._gpx.tracks) == 0:
            raise ValueError("No tracks found.")
        self._filename = os.path.basename(filename)
        self._gpxid = self._gpx.tracks[0].name
        logger.info(f"Parsed gpx file with id {self._gpxid}.")

    def route_data(self) -> pd.DataFrame:
        """Convert gpx to pandas data frame."""
        if len(self._gpx.tracks[0].segments) == 0:
            raise ValueError("No track segments found.")

        points = []
        for segment in self._gpx.tracks[0].segments:
            for point in segment.points:
                hr = None
                accuracy = None
                for e in point.extensions:
                    for i in e:
                        if "hr" in i.tag:
                            hr = int(i.text)
                        elif "accuracy" in i.tag:
                            accuracy = float(i.text)
                points.append(
                    {
                        "lon": point.longitude,
                        "lat": point.latitude,
                        "alt": point.elevation,
                        "time": point.time,
                        "hr": hr,
                        "acc": accuracy,
                    }
                )

        df = pd.DataFrame(points)
        logger.debug(df)
        self._df = df
        return df

    def enrich(self) -> pd.DataFrame:
        """Adds columns to the GPX data.

        - delta_t: time in seconds between GPX points (typically constant)
        - t: time in seconds from the first GPX point (cumulative of delta_t)
        - delta_2d: 2D distance travelled between two consecutive GPX points
        - delta_3d: 3D distance travelled between two consecutive GPX points
        - 2d: cumulative 2D distance travelled
        - 3d: cumulative 3D distance travelled
        - speed: delta_2d / delta_t
        """
        df = self._df
        if df is None:
            df = self.route_data()
        assert df is not None

        try:
            logger.debug("convert time to seconds for calculations")
            df["timestamp"] = df.apply(lambda row: row["time"].timestamp(), axis=1)
        except KeyError:
            df["timestamp"] = df.index
        logger.debug(df.head())

        logger.debug("time as index")
        df = df.set_index("time")

        logger.debug("data including null values")
        df_null = df[df.isnull().any(axis=1)]
        logger.debug(df_null.head())

        logger.debug("sort by time")
        df = df.sort_index()
        logger.debug(df.head())
        logger.debug(":")
        logger.debug(df.tail())

        logger.debug("calculate distance")
        df["delta_t"] = (df.timestamp - df.timestamp.shift()).fillna(0)
        df["t"] = df["delta_t"].cumsum()
        hav2d = [0.0]
        hav3d = [0.0]
        for i in range(len(df)):
            if i == 0:
                continue
            a = (df.iloc[i - 1].lat, df.iloc[i - 1].lon)
            b = (df.iloc[i].lat, df.iloc[i].lon)
            hav2d.append(haversine.haversine(a, b, unit=haversine.Unit.METERS))
            dalt = df.iloc[i].alt - df.iloc[i - 1].alt
            hav3d.append(math.sqrt(hav2d[-1] ** 2 + dalt**2))
        df["delta_2d"] = hav2d
        df["delta_3d"] = hav3d
        df["2d"] = df["delta_2d"].cumsum()
        df["3d"] = df["delta_3d"].cumsum()
        df["speed"] = df["delta_2d"] / df["delta_t"]

        logger.debug(df)
        self._df = df
        return df

    def summary(self) -> Summary:
        """Returns some statistics."""
        df = self._df
        if df is None or "2d" not in df.columns:
            logger.debug("Enrich GPX data first.")
            df = self.enrich()
        assert self._gpxid is not None, "Something already went wrong at parsing."

        stats = Summary(
            id=self._gpxid,
            date=df.index[0],
            timeSeconds=df.iloc[-1]["t"],
            distanceMeters=df.iloc[-1]["2d"],
        )

        stats.fill_defaults()
        stats.activity = Activity.guess(self._gpxid, stats.speedMetersPerSecond)

        return stats
