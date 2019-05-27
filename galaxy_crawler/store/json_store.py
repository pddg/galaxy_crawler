import codecs
import json
from collections import OrderedDict
from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING
from pytz import timezone

from galaxy_crawler import errors
from galaxy_crawler.repositories import ResponseDataStore

if TYPE_CHECKING:
    from typing import Any, Union
    from pathlib import Path

logger = getLogger(__name__)

datetime_format = "%Y-%m-%dT%H:%M%z"


def _serialize(o):
    if isinstance(o, datetime):
        return o.strftime(datetime_format)
    raise TypeError(repr(o) + " is not JSON serializable")


class JsonDataStore(ResponseDataStore):
    file_name = "repositories.json"

    def __init__(self, output_dir: 'Path'):
        self.output_dir = output_dir
        self.output_file = output_dir / self.file_name
        if self.output_file.exists():
            with codecs.open(str(self.output_file), 'r', 'utf-8') as fp:
                self.repositories = json.load(fp)
            self.repositories['start_at'] = datetime.strptime(self.repositories['start_at'], datetime_format)
            self.repositories['finished_at'] = datetime.strptime(self.repositories['finished_at'], datetime_format)
        else:
            now = timezone('Asia/Tokyo').localize(datetime.now())
            self.repositories = dict({
                "start_at": now,
                "finished_at": now,
                "repositories": dict()
            })

    def exists(self, key: 'Union[int, str]') -> bool:
        if isinstance(key, int):
            key = str(key)
        if key in self.repositories['repositories']:
            return True
        return False

    def get(self, key: 'Union[int, str]') -> 'dict':
        if isinstance(key, int):
            key = str(key)
        if self.exists(key):
            return self.repositories['repositories'][key]
        raise errors.NoSuchRecord

    def get_all(self) -> 'OrderedDict':
        return OrderedDict(self.repositories['repositories'])

    def save(self, obj: 'dict', commit: bool = False) -> 'Any':
        if "id" not in obj:
            raise errors.NoPrimaryKeyError

        primary_key = str(obj['id'])
        if self.exists(primary_key):
            logger.warning(f"Override the item number {primary_key}")
        self.repositories['repositories'][primary_key] = obj
        if commit:
            self.commit()

    def commit(self):
        with codecs.open(str(self.output_file), 'w', 'utf-8') as fp:
            json.dump(self.repositories, fp, default=_serialize)
