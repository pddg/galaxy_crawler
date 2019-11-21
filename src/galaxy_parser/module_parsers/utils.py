import email
import shlex

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


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
    command = email.utils.unquote(command)
    splitted = command.split('/')
    return splitted[-1]
