from typing import TYPE_CHECKING

from .base import ModuleArgs, BaseCommandModuleParser

if TYPE_CHECKING:
    from typing import Union


class CommandArgs(ModuleArgs):
    def __init__(self, **kwargs):
        super(CommandArgs, self).__init__(**kwargs)
        self.creates = kwargs.get('creates')
        self.chdir = kwargs.get('chdir')
        self.removes = kwargs.get('removes')
        self.stdin = kwargs.get('stdin')
        self.stdin_add_newline = kwargs.get('stdin_add_newline', True)
        self.strip_empty_ends = kwargs.get('strip_empty_ends', True)
        self.warn = kwargs.get('warn', True)


def _parse_command(cmd: 'Union[dict, str]') -> 'str':
    if isinstance(cmd, str):
        return cmd
    if not isinstance(cmd, dict):
        raise TypeError(f'dict type is expected, but actual "{cmd.__class__.__name__}"')
    if 'cmd' in cmd:
        return cmd.get('cmd')
    return ' '.join(cmd.get('argv'))


class CommandModuleParser(BaseCommandModuleParser):
    """
    Ansible command module - Execute commands on targets
    https://docs.ansible.com/ansible/2.9/modules/command_module.html
    """

    name = 'command'
    args_class = CommandArgs

    def __init__(self, **kwargs):
        super(CommandModuleParser, self).__init__(**kwargs)
        self.command = _parse_command(kwargs.get(self.name)).strip()
