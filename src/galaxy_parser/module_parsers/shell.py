from typing import TYPE_CHECKING

from .base import ModuleArgs, BaseCommandModuleParser

if TYPE_CHECKING:
    from typing import Union


class ShellArgs(ModuleArgs):

    def __init__(self, **kwargs):
        super(ShellArgs, self).__init__(**kwargs)
        self.executable = kwargs.get('executable')
        self.creates = kwargs.get('creates')
        self.chdir = kwargs.get('chdir')
        self.removes = kwargs.get('removes')
        self.stdin = kwargs.get('stdin')
        self.stdin_add_newline = kwargs.get('stdin_add_newline', True)
        self.warn = kwargs.get('warn', True)


def _parse_command(cmd: 'Union[str, dict]') -> 'str':
    if isinstance(cmd, str):
        return cmd
    if not isinstance(cmd, dict):
        raise TypeError(f'dict type is expected, but actual "{cmd.__class__.__name__}"')
    return cmd.get('cmd', '')


class ShellModuleParser(BaseCommandModuleParser):
    """
    Ansible shell module - Execute shell commands on targets
    https://docs.ansible.com/ansible/2.9/modules/shell_module.html
    """

    name = 'shell'

    args_class = ShellArgs

    def __init__(self, **kwargs):
        super(ShellModuleParser, self).__init__(**kwargs)
        self.command = _parse_command(kwargs.get(self.name)).strip()
