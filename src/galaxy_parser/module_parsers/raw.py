from .base import ModuleArgs, BaseCommandModuleParser
from .utils import split_command


class RawArgs(ModuleArgs):
    def __init__(self, **kwargs):
        super(RawArgs, self).__init__(**kwargs)
        self.executable = kwargs.get('executable')


class RawModuleParser(BaseCommandModuleParser):
    """
    Ansible raw module - Executes a low-down and dirty command
    https://docs.ansible.com/ansible/2.9/modules/raw_module.html
    """

    name = 'raw'
    args_class = RawArgs

    def __init__(self, **kwargs):
        super(RawModuleParser, self).__init__(**kwargs)
        self.command = split_command(kwargs.get(self.name))
