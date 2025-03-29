#!/usr/bin/env python3

# %% imports
from datetime import datetime
import logging
import os
import pandas as pd
import xmltodict

from .activity import Activity
from .summary import Summary

logger = logging.getLogger(__name__)


class TCXParser:
    def __init__(self):
        # default values
        self._filename: str | None = None
        self._id: str | None = None
        self._df: pd.DataFrame | None = None

    @property
    def filename(self) -> str | None:
        return self._filename

    @property
    def id(self) -> str | None:
        return self._id

    def parse(self, filename):
        """Parse tcx file."""
        with open(filename, "r") as f:
            data = f.read()
        self._tcx = xmltodict.parse(data)
        try:
            self._id = self._tcx["TrainingCenterDatabase"]["Activities"]["Activity"][
                "Id"
            ]
            logger.info(f"Parsed tcx file with id {self._id}.")
            self._filename = os.path.basename(filename)
        except KeyError:
            raise ValueError("No id found.")

    def summary(self) -> Summary:
        """Returns some statistics."""
        assert self._id is not None, "Something already went wrong at parsing."

        try:
            lap = self._tcx["TrainingCenterDatabase"]["Activities"]["Activity"]["Lap"]
            start_time = lap["@StartTime"]
            durationSeconds = lap["TotalTimeSeconds"]
            distanceMeters = lap["DistanceMeters"]
        except KeyError:
            raise ValueError("No activity/lap data found.")

        stats = Summary(
            id=self._id,
            date=datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ"),
            timeSeconds=int(durationSeconds),
            distanceMeters=float(distanceMeters),
        )

        stats.fill_defaults()
        stats.activity = Activity.guess(self._filename, stats.speedMetersPerSecond)

        return stats
