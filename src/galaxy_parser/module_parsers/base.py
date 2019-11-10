from typing import TYPE_CHECKING

from .utils import get_base_name, is_tmpl_variable

if TYPE_CHECKING:
    from typing import Dict, Tuple


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

    @classmethod
    def parse(cls, task: 'Dict[str, str]') -> 'ModuleParser':
        return cls(**task)

    def get_args(self) -> 'dict':
        return self._kwargs.get('args', dict())


class BaseCommandModuleParser(ModuleParser):

    def get_command(self) -> 'Tuple[str, bool]':
        """
        Returns the execution command itself without any arguments.
        Returns the basename of the path if it is indicated by an absolute/relative path.
        If a template variable is used in the execution command, the second return value will be True.
        For example:
            'echo "Hello world"' -> ("echo", False)
            '/bin/echo "Hello world"' -> ("echo", False)
            './bin/echo "Hello world"' -> ("echo", False)
            'echo "{{ message }}"' -> ("echo", False)
            '{{ echo_cmd }} "Hello world"' -> ("{{ echo_cmd }}", True)
            '/bin/{{ echo_cmd }} "Hello world"' -> ("{{ echo_cmd }}", True)
        :return: Command name and whether a template variable is used
        """
        base_command = get_base_name(self.command[0])
        is_var = is_tmpl_variable(base_command)
        return base_command, is_var

