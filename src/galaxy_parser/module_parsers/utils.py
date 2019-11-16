import re
import shlex

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

tmpl_var_re = re.compile(r'{{.+}}')


def _assert_is_str(s: str):
    if not isinstance(s, str):
        raise TypeError(f'str type is expected, but actual "{s.__class__.__name__}"')


def split_command(command: str) -> 'List[str]':
    """
    Split command into list of arguments.
    eg. echo "Hello world" -> ['echo', '"Hello world"']
    :param command: Executable commands which contains arguments
    :return: The list of command line arguments
    """
    _assert_is_str(command)
    return shlex.split(command)


def get_base_name(command: str) -> str:
    """
    Return basename of command.
    eg. /bin/echo "Hello world" -> 'echo'
    :param command: Executable command path
    :return: Basename of command
    """
    _assert_is_str(command)
    splitted = command.split('/')
    return splitted[-1]


def find_command(divided_command: 'List[str]') -> str:
    """
    Find the command from divided command list with Jinja2 style variable
    e.g. ["{{", "hoge", "}}", "fuga"] -> "{{ hoge }}"
    :param divided_command:
    :return:
    """
    assert len(divided_command) > 0
    base_name = get_base_name(divided_command[0])
    if base_name.startswith('{{'):
        if base_name.endswith('}}'):
            return base_name
        commands = [base_name]
        for c in divided_command[1:]:
            c = c.strip()
            commands.append(c)
            if c.endswith('}}'):
                return ' '.join(commands)
            elif (c.startswith('}}') or '}}' in c) and len(c) > 2:
                return find_command(c.split('}')[2:] + divided_command[len(commands):])
    return base_name


def is_tmpl_variable(chars: str) -> bool:
    """
    If given chars are template variable (Jinja2 syntax)
    :param chars: Any string
    :return: Whether the given sentence is a template variable or not
    """
    _assert_is_str(chars)
    if tmpl_var_re.match(chars):
        return True
    return False
