from .base import ModuleArgs, BaseCommandModuleParser
from .utils import split_command


class ScriptArgs(ModuleArgs):

    def __init__(self, **kwargs):
        super(ScriptArgs, self).__init__(**kwargs)
        self.chdir = kwargs.get('chdir')
        self.creates = kwargs.get('creates')
        self.decrypt = kwargs.get('decrypt', True)
        self.executable = kwargs.get('executable')
        self.removes = kwargs.get('removes')


class ScriptModuleParser(BaseCommandModuleParser):
    """
    Ansible script module - Runs a local script on a remote node after transferring it
    https://docs.ansible.com/ansible/2.9/modules/script_module.html
    """

    name = 'script'
    args_class = ScriptArgs

    def __init__(self, **kwargs):
        super(ScriptModuleParser, self).__init__(**kwargs)
        self.command = split_command(kwargs.get(self.name))
