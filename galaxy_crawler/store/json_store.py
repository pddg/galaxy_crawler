import codecs
import json
import copy
from collections import OrderedDict
from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING
from pytz import timezone

from galaxy_crawler.repositories import ResponseDataStore

if TYPE_CHECKING:
    from typing import Any, Union, List
    from pathlib import Path
    from galaxy_crawler.constants import Target

logger = getLogger(__name__)

datetime_format = "%Y-%m-%dT%H:%M%z"


def _serialize(o):
    if isinstance(o, datetime):
        return o.strftime(datetime_format)
    raise TypeError(repr(o) + " is not JSON serializable")


class Counter(object):

    def __init__(self):
        self._memory = dict()

    def increment(self, key: str):
        if key in self._memory:
            self._memory[key] += 1
        else:
            self._memory[key] = 0

    def get_count(self, key: 'str') -> int:
        if key in self._memory:
            return self._memory[key]
        self._memory[key] = 0
        return 0


class JsonDataStore(ResponseDataStore):

    def __init__(self, output_dir: 'Path'):
        self.output_dir = output_dir
        self.counter = Counter()
        now = self._get_current_time()
        self.template = {
            "start_at": now,
            "finished_at": now,
            "json": []
        }
        self.responses = dict()

    def _get_current_time(self):
        return timezone('Asia/Tokyo').localize(datetime.now())

    def save(self, target: 'Target', obj: 'List[dict]', commit: bool = False) -> 'Any':
        if target.value in self.responses:
            self.responses[target.value]['json'].extend(obj)
            self.responses[target.value]['finished_at'] = self._get_current_time()
        else:
            tmpl = copy.deepcopy(self.template)
            tmpl['json'] = obj
            tmpl['finished_at'] = self._get_current_time()
            self.responses[target.value] = tmpl
        if commit:
            self.commit()

    def initialize(self):
        self.responses = dict()

    def commit(self):
        for name, value in self.responses.items():
            count = self.counter.get_count(name)
            f = self.output_dir / name / f"{name}_{count}.json"
            if not f.parent.exists():
                f.parent.mkdir(parents=True)
            with codecs.open(str(f), 'w', 'utf-8') as fp:
                json.dump(value, fp, default=_serialize)
            self.counter.increment(key=name)
        self.responses = dict()
