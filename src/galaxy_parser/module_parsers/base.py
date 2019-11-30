import logging
from typing import TYPE_CHECKING

from bashlex import errors

from galaxy_parser.script_parsers import (
    is_tmpl_var,
    fill_variable,
    as_ast,
    CommandParser,
)
from .utils import get_base_name

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

    @classmethod
    def parse(cls, task: 'Dict[str, str]') -> 'ModuleParser':
        return cls(**task)

    def set_parent_block(self, block: 'Block'):
        self._parent = block

    def get_parent_block(self) -> 'Block':
        return self._parent

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


class GeneralModuleParser(ModuleParser):
    """Subclass of Module parser for global module parsing"""
    pass


class BaseCommandModuleParser(ModuleParser):

    def get_commands(self) -> 'List[Tuple[str, bool]]':
        """
        Returns the execution command itself without any arguments.
        Returns the basename of the path if it is indicated by an absolute/relative path.
        If a template variable is used in the execution command, the second return value will be True.
        For example:
            'echo "Hello world"' -> [("echo", False)]
            '/bin/echo "Hello world"' -> [("echo", False)]
            './bin/echo "Hello world"' -> [("echo", False)]
            'echo "{{ message }}"' -> [("echo", False)]
            '{{ echo_cmd }} "Hello world"' -> [("ANSIBLE_VAR_UNDEF", True)]
            '/bin/{{ echo_cmd }} "Hello world"' -> [("ANSIBLE_VAR_UNDEF", True)]
        :return: Command name and whether a template variable is used
        """
        command = self.command
        command = fill_variable(command)
        command = command.replace('\n', ' ')
        command = command.replace('\r', '')
        try:
            trees = as_ast(command)
        except (errors.ParsingError, NotImplementedError) as e:
            logger.warning(f"Failed to parse by bashlex({e}): '{command}'")
            # Try to use heuristic approach
            command = get_base_name(self.command)
            return [(command, is_tmpl_var(command))]
        commands = []
        for tree in trees:
            parser = CommandParser()
            parser.visit(tree)
            commands.extend(parser.get_commands())
        return [(get_base_name(c), is_tmpl_var(c)) for c in commands]
