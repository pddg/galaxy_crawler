import email
import shlex

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Union, Type
    from .base import ModuleParser


def _assert_is_str(s: str):
    if not isinstance(s, str):
        raise TypeError(f'str type is expected, but actual "{s.__class__.__name__}"')


def parse_task(task: 'dict', parsers: 'Dict[str, Type[ModuleParser]]', default_parser: 'Type[ModuleParser]'):
    """
    Parse a task with given parsers.
    :param task: Dictionary of task
    :param parsers: ModuleParsers to use
    :param default_parser: Default parser for modules
    :return: Parsed task as an instance of ModuleParser
    """
    parser = None
    for name in parsers.keys():
        if name in task.keys():
            parser = parsers[name]
            break
    if parser is None:
        # Try to parse with general parser if there is no appropriate parser.
        parser = default_parser
    return parser(**task)


def normalize_condition(when: 'Union[str, List[str]]') -> 'str':
    """
    Normalize `when` directive.
    For example:
        'hoge is fuga' -> 'hoge is fuga'
        ['hoge is fuga', 'poyo is fuga'] -> 'hoge is fuga and poyo is fuga'
    :param when: A condition to normalize
    :return: Normalized string
    """
    if isinstance(when, list):
        return " and ".join([str(w) for w in when])
    return when


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
    command = email.utils.unquote(command)
    splitted = command.split('/')
    return splitted[-1]
