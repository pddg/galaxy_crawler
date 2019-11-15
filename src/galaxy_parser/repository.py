import hashlib
import logging
from typing import TYPE_CHECKING

import git
import yaml
import yaml.constructor
import yaml.parser

from . import monorepo
from . import utils

if TYPE_CHECKING:
    from typing import Union, Optional, List
    from pathlib import Path

logger = logging.getLogger(__name__)


class YAMLFile(object):

    def __init__(self, path: 'Union[str, Path]'):
        self.path = utils.to_path(path)
        self.base_dir = self.path.parent
        if not self.path.exists():
            raise FileNotFoundError(f"'{self.path}' does not exists.")
        with self.path.open('r', encoding='utf-8') as f:
            try:
                self.content = yaml.load(f, Loader=yaml.UnsafeLoader)
            except yaml.parser.ParserError as e:
                logger.error(f"'{self.path}' has a invalid syntax. '{e}'")
                self.content = None
        # If the YAML has no content
        if self.content is None:
            self.content = []

    def __add__(self, other: 'YAMLFile'):
        assert isinstance(other, self.__class__)
        if other.content is None:
            return self
        self.content += other.content
        return self


def _get_yaml_recursively(base_dir: 'Path') -> 'List[Path]':
    yml_files = list(base_dir.glob('**/*.yml'))
    yaml_files = list(base_dir.glob('**/*.yaml'))
    return yml_files + yaml_files


class Repository(object):
    """
    Representation of repository.
    This is a singleton class per repository and thread safe.
    DO NOT USE WITH MULTIPROCESSING.
    """

    def __init__(self, repository_path: 'Union[str, Path]'):
        self.path = utils.to_path(repository_path)
        self.repository = git.Repo(str(self.path))
        self.role_finder = monorepo.RoleFinder(self.path)
        # If the repository is monorepo, search all roles in it.
        if self.role_finder.is_monorepo():
            self.role_finder.construct_map()

    def checkout(self, version: str):
        try:
            self.repository.git.checkout(version)
            self._debug(f"Checkout version {version}")
        except Exception as e:
            self._error(f"Checkout failed due to '{e.__class__.__name__}: {e}'")

    def get_yaml(self, dir_name: 'str', role_name: 'Optional[str]' = None) -> 'Optional[YAMLFile]':
        """
        Concat all YAML file in the specified sub directory
        If the parser failed to load YAML file, skip it and return empty YAMLFile instance.
        :param dir_name:    Specify the sub dir name. (tasks, handlers, ...)
        :param role_name:   Specify the role name. If the repository is a monorepo structure,
                            find the specified role and return YAML in it.
        :return:            Concatenated YAML Files
        """
        if role_name is not None:
            role_path = self.role_finder.find(role_name)
        else:
            role_path = self.path
        base_dir = role_path / dir_name
        yaml_files = _get_yaml_recursively(base_dir)
        yaml_content = None
        for yml in yaml_files:
            try:
                if yaml_content is None:
                    yaml_content = YAMLFile(yml)
                else:
                    yaml_content += YAMLFile(yml)
            except yaml.constructor.ConstructorError as e:
                self._error(f"YAML parse failed due to '{e}'")
                continue
        return yaml_content

    def is_monorepo(self):
        """Whether the repository has monorepo structure"""
        return self.role_finder.is_monorepo()

    def _log(self, msg: str, level: int):
        logger.log(level, f"{self.path.parent.name}/{self.path.name}: {msg}")

    def _debug(self, msg: str):
        self._log(msg, logging.DEBUG)

    def _error(self, msg: str):
        self._log(msg, logging.ERROR)

    def identify(self) -> 'str':
        """
        Returns the identity hash (SHA1)
        :return: Hash string
        """
        return hashlib.sha1(str(self.path).encode('utf-8')).hexdigest()

    def cleanup(self):
        self.repository.close()
