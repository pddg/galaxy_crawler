from typing import TYPE_CHECKING

from .base import ModuleArgs, BaseCommandModuleParser

if TYPE_CHECKING:
    from typing import Union


class ScriptArgs(ModuleArgs):

    def __init__(self, **kwargs):
        super(ScriptArgs, self).__init__(**kwargs)
        self.chdir = kwargs.get('chdir')
        self.creates = kwargs.get('creates')
        self.decrypt = kwargs.get('decrypt', True)
        self.executable = kwargs.get('executable')
        self.removes = kwargs.get('removes')


def _parse_command(cmd: 'Union[str, dict]') -> 'str':
    if isinstance(cmd, str):
        return cmd
    if not isinstance(cmd, dict):
        raise TypeError(f'dict type is expected, but actual "{cmd.__class__.__name__}"')
    return cmd.get('cmd', '')


class ScriptModuleParser(BaseCommandModuleParser):
    """
    Ansible script module - Runs a local script on a remote node after transferring it
    https://docs.ansible.com/ansible/2.9/modules/script_module.html
    """

    name = 'script'
    args_class = ScriptArgs

    def __init__(self, **kwargs):
        super(ScriptModuleParser, self).__init__(**kwargs)
        self.command = _parse_command(kwargs.get(self.name)).strip()
