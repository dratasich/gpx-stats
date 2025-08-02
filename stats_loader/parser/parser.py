"""Abstract parser class for parsing activity files."""

from datetime import UTC, datetime

import pandas as pd

from .file import File
from .summary import Summary


class Parser:
    @property
    def id(self):
        raise NotImplementedError

    @property
    def filename(self):
        raise NotImplementedError

    def parse(self, filename: str):
        raise NotImplementedError

    def summary(self) -> Summary:
        raise NotImplementedError

    def locations(self) -> pd.DataFrame:
        raise NotImplementedError

    @property
    def metadata(self) -> File:
        return File(
            id=self.id,
            loaded=datetime.now(UTC),
            basename=self.filename,
        )
