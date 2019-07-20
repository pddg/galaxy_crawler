import re
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy.engine import create_engine

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


def get_in_memory_database() -> 'Engine':
    return create_engine("sqlite://", echo=True)


class InvalidUrlError(Exception):

    def __init__(self, url: str, backend: str):
        self.url = url
        self.backend = backend.lower()

    def __str__(self):
        return f"'{self.url}' is invalid for the backend ({self.backend})"


class EngineType(Enum):

    IN_MEMORY = r'^sqlite://$'
    POSTGRES = r'^postgresql\:\/\/([^\/]+(\:[^\/]+)?@)?[^\/]+\:[0-9]+\/.+$'
    SQLITE = r'^sqlite\:\/\/\/\/?.+$'

    @classmethod
    def from_url(cls, url: str):
        for c in cls:
            reg = re.compile(c.value)
            if reg.match(url):
                return cls[c.name]
        raise InvalidUrlError(url, "not specified")

    def get_engine(self, url):
        reg = re.compile(self.value)
        if reg.match(url):
            engine = create_engine(url)
        else:
            raise InvalidUrlError(url, self.name)
        return engine
