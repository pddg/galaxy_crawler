from typing import TYPE_CHECKING

from . import utils
from .base import GeneralModuleParser

if TYPE_CHECKING:
    from typing import List, Optional, Union, Dict, Type
    from .base import ModuleParser


class Block(object):
    """Representation for block directive"""

    name = 'block'
    kind = 'block'

    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._tasks = []  # type: List[Union[ModuleParser, Block]]
        self._rescue_tasks = []  # type: List[Union[ModuleParser, Block]]
        self._when = utils.normalize_condition(kwargs.get('when', None))

        # Parent block link
        self._parent = None  # type: Optional[Block]
        # The path to file in which the task is written
        self._file = None  # type: Optional[str]
        # This block is used as handler
        self._is_handler = False

    def _parse(self, task: 'dict', parsers: 'Dict[str, Type[ModuleParser]]') -> 'Union[ModuleParser, Block]':
        if self.name in task:
            block = Block(**task)
            block.set_parent(self)
            block.parse(parsers)
            return block
        task = utils.parse_task(task, parsers, GeneralModuleParser)
        task.set_parent_block(self)
        return task

    def parse(self, parsers: 'Dict[str, Type[ModuleParser]]'):
        self._tasks = []
        self._rescue_tasks = []
        for task in self._kwargs.get('block', [self._kwargs]):
            parsed = self._parse(task, parsers)
            self._tasks.append(parsed)
        for task in self._kwargs.get('rescue', []):
            parsed = self._parse(task, parsers)
            self._rescue_tasks.append(parsed)

    def set_parent(self, parent: 'Block'):
        self._parent = parent

    def set_file(self, filepath: str):
        self._file = filepath

    def set_as_handler(self):
        self._is_handler = True

    def get_tasks(self) -> 'List[Union[ModuleParser, Block]]':
        return self._tasks

    def get_rescue_tasks(self) -> 'List[Union[ModuleParser, Block]]':
        return self._rescue_tasks

    def get_all_tasks(self) -> 'List[Union[ModuleParser, Block]]':
        return self._tasks + self._rescue_tasks

    def _get_flatten(self, target: str) -> 'List[ModuleParser]':
        tasks = []
        for task in getattr(self, f'get_{target}_tasks', self.get_tasks)():
            if isinstance(task, Block):
                _tasks = getattr(task, f'get_{target}_tasks_flatten', task.get_tasks_flatten)()
                tasks.extend(_tasks)
            else:
                tasks.append(task)
        return tasks

    def get_tasks_flatten(self) -> 'List[ModuleParser]':
        return self._get_flatten('regular')

    def get_rescue_tasks_flatten(self) -> 'List[ModuleParser]':
        return self._get_flatten('rescue')

    def get_all_tasks_flatten(self) -> 'List[ModuleParser]':
        return self._get_flatten('all')

    def has_when(self) -> 'bool':
        if self._when is not None:
            return True
        if self._parent is not None:
            return self._parent.has_when()
        return False

    def is_handler(self) -> 'bool':
        if self._is_handler:
            return True
        if self._parent is not None:
            return self._parent.is_handler()
        return False
