import logging
from typing import TYPE_CHECKING

import yaml
from .utils import parse_commands

if TYPE_CHECKING:
    from typing import Dict, Tuple, List, Optional
    from .block import Block

logger = logging.getLogger(__name__)


class ModuleArgs(object):
    """
    Free arguments for Ansible module
    """

    def __init__(self, **kwargs):
        self._kwargs = kwargs


class ModuleParser(object):
    """
    Base parser for all modules. Common options are implemented.
    """

    name = None

    args_class = ModuleArgs

    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self.task_name = kwargs.get('name')
        self.when = kwargs.get('when')
        self.changed_when = kwargs.get('changed_when')
        self.failed_when = kwargs.get('failed_when')
        self.delegate_to = kwargs.get('delegate_to')
        self.register = kwargs.get('register')
        self.become = kwargs.get('become', False)
        self.become_user = kwargs.get('become_user', 'root')
        self.args = self.args_class(**self.get_args())
        self._parent = None  # type: Optional[Block]
        self._file = None  # type: Optional[str]

    @classmethod
    def parse(cls, task: 'Dict[str, str]') -> 'ModuleParser':
        return cls(**task)

    def set_parent_block(self, block: 'Block'):
        self._parent = block

    def get_parent_block(self) -> 'Block':
        return self._parent

    def set_file(self, filepath: str):
        self._file = filepath

    def has_when(self) -> 'bool':
        if self.when is not None:
            return True
        parent = self.get_parent_block()
        if parent is None:
            return False
        return parent.has_when()

    def is_handler(self) -> 'bool':
        parent = self.get_parent_block()
        if parent is None:
            return False
        return parent.is_handler()

    def get_args(self) -> 'dict':
        return self._kwargs.get('args', dict())

    def as_yaml(self) -> 'str':
        return yaml.dump(self._kwargs, sort_keys=False)


class GeneralModuleParser(ModuleParser):
    """Subclass of Module parser for global module parsing"""
    pass


class BaseCommandModuleParser(ModuleParser):

    def get_commands(self) -> 'List[Tuple[str, bool]]':
        return parse_commands(self.name, self.command)
