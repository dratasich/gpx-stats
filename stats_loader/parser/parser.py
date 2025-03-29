"""Abstract parser class for parsing activity files."""


class Parser:
    @property
    def id(self):
        raise NotImplementedError

    @property
    def filename(self):
        raise NotImplementedError

    def parse(self, filename: str):
        raise NotImplementedError

    def summary(self):
        raise NotImplementedError
