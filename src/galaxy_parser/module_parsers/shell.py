from .base import ModuleArgs, BaseCommandModuleParser


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


class ShellModuleParser(BaseCommandModuleParser):
    """
    Ansible shell module - Execute shell commands on targets
    https://docs.ansible.com/ansible/2.9/modules/shell_module.html
    """

    name = 'shell'

    args_class = ShellArgs

    def __init__(self, **kwargs):
        super(ShellModuleParser, self).__init__(**kwargs)
        self.command = kwargs.get(self.name).strip()
