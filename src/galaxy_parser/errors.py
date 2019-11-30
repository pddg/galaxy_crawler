from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union
    from pathlib import Path


class RepositoryNotFound(Exception):
    """Specified repository cannot be cloned."""

    def __init__(self, repo_path: 'Union[str, Path]'):
        self.path = repo_path

    def __str__(self):
        return f"'{self.path}' does not exist. It may be removed from GitHub or you do not clone it."


class NoTasks(Exception):
    """There is no tasks in the specified role"""

    def __init__(self, role_name: 'str', path: 'Union[str, Path]'):
        self.role_name = role_name
        self.path = path

    def __str__(self):
        return f"There is no tasks '{self.role_name}' ('{self.path}')"


class NoSuchRole(Exception):
    """There is no such name role"""

    def __init__(self, role_name: 'str', path: 'Union[str, Path]'):
        self.role_name = role_name
        self.path = path

    def __str__(self):
        return f"There is no role named '{self.role_name}' in '{self.path}'"


class NoMetaData(Exception):
    """The role has no metadata"""
    pass


