import email
import logging
import shlex
from typing import TYPE_CHECKING

from bashlex import errors

from galaxy_parser.script_parsers import (
    is_tmpl_var,
    fill_variable,
    as_ast,
    CommandParser,
)

if TYPE_CHECKING:
    from typing import List, Dict, Union, Type, Tuple
    from .base import ModuleParser

logger = logging.getLogger(__name__)


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


def parse_commands(module_type: str, script: str) -> 'List[Tuple[str, bool]]':
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
    script = fill_variable(script)
    # To support block type multiline charactes with extra indent.
    # For example:
    # a: >
    #   b
    #    c
    # This may interpreted as `{'a': 'b\n c\n'}` in YAML 1.1
    # bashlex will parse it as the script with 2 commands (`b` and `c`).
    # However, Ansible's `command` module split them at a new line or
    # a white space and use the list of tokens to execute.
    if module_type == 'command':
        script = script.replace("\n", " ").replace("\r", "")
    try:
        trees = as_ast(script)
    except (errors.ParsingError, NotImplementedError) as e:
        logger.warning(f"Failed to parse by bashlex({e}): '{script}'")
        # Try to use heuristic approach
        command = get_base_name(script)
        return [(command, is_tmpl_var(command))]
    commands = []
    for tree in trees:
        parser = CommandParser()
        parser.visit(tree)
        commands.extend(parser.get_commands())
    return [(get_base_name(c), is_tmpl_var(c)) for c in commands]
