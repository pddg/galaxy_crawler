from datetime import datetime
from typing import TYPE_CHECKING

from pytz import timezone

from galaxy_crawler.errors import DateParseFailed

if TYPE_CHECKING:
    from pathlib import Path


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
SECONDARY_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
UTC = timezone('UTC')


def as_utc(d: 'datetime') -> 'datetime':
    if d.tzinfo is not None:
        return d.astimezone(UTC)
    return UTC.localize(d)


def to_datetime(d_str: 'str') -> 'datetime':
    if isinstance(d_str, datetime):
        return d_str
    try:
        dt_obj = datetime.strptime(d_str, DATETIME_FORMAT)
    except ValueError:
        try:
            dt_obj = datetime.strptime(d_str, SECONDARY_DATETIME_FORMAT)
        except ValueError as e:
            raise DateParseFailed(str(e))
    except TypeError:
        return None
    return as_utc(dt_obj)



def to_absolute(path: 'Path'):
    if path is None:
        raise ValueError("Path must not be `None`")
    path = path.expanduser()
    if not path.is_absolute():
        path = path.absolute()
    return path


def mkdir(path: 'Path'):
    path = to_absolute(path)
    if not path.exists():
        path.mkdir(parents=True)
    else:
        if path.is_file():
            raise NotADirectoryError(f"'{path}' is not a directory.")
    return path
