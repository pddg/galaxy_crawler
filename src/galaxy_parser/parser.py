import logging
from typing import TYPE_CHECKING

import yaml
from git import Repo
from yaml.constructor import ConstructorError
from yaml.parser import ParserError

from . import utils

if TYPE_CHECKING:
    from typing import Union, Dict, Optional, List, Type
    from pathlib import Path

    from .module_parsers import ModuleParser
    from galaxy_crawler.models.v1 import Role

logger = logging.getLogger(__name__)


class TaskParser(object):
    """
    Parse all tasks in a Role
    """
    block_directives = [
        'block',
        'rescue'
    ]

    parse_targets = [
        'tasks',
        'handlers'
    ]

    def __init__(self, role: 'Role', ghq_root: 'Union[str, Path]'):
        self.role = role
        self._ghq_root = utils.to_path(ghq_root)
        self._role_path = self._ghq_root / utils.to_role_path(role.repository.clone_url)
        self.repo = Repo(str(self._role_path))
        self.parsers = dict()  # type: Dict[str, Type[ModuleParser]]
        self.role_name = f"{self.role.namespace.name}/{self.role.name}"

    def set_parser(self, *parsers: 'Type[ModuleParser]'):
        for parser in parsers:
            name = parser.name
            self.parsers[name] = parser

    def _concat_yaml(self, target: 'str') -> 'Optional[YAMLFile]':
        target_path = self._role_path / target
        if not target_path.exists():
            return None
        yml_file = None
        ymls = list(target_path.glob('*.yml')) + list(target_path.glob('*.yaml'))
        for yml in ymls:
            logger.debug(f'Load YAML: {yml}')
            try:
                current_yml = YAMLFile(yml)
            except ConstructorError as e:
                logger.error(f"{self.role_name}: YAML parse failed due to '{e}'")
                continue
            if yml_file is None:
                yml_file = current_yml
            else:
                yml_file += current_yml
        return yml_file

    def _parse(self, task: dict) -> 'List[ModuleParser]':
        parsed_tasks = []
        # If this task is a block or rescue directive
        for div in self.block_directives:
            if div in task:
                for t in task[div]:
                    parsed = self._parse(t)
                    parsed_tasks.extend(parsed)
        # Find appropriate parser
        parser = None
        for name in self.parsers.keys():
            if name in task.keys():
                parser = self.parsers[name]
                break
        if parser is None:
            return parsed_tasks
        try:
            parsed_tasks.append(parser(**task))
        except Exception as e:
            logger.error(f"{self.role_name}: Task parse failed due to '{e}'")
        return parsed_tasks

    def _checkout(self, version: 'str'):
        logger.debug(f'Checkout: {self.role_name} -> {version}')
        self.repo.git.checkout(version)

    def parse(self, version: 'Optional[str]' = None) -> 'List[ModuleParser]':
        """
        Parse all YAML file in Role. Parse by given ModuleParser.
        :param version: Branch or tag, commit hash to checkout
        :return: Parsed modules
        """
        if version is None:
            # Checkout latest release
            latest = self.role.get_stable_version()
            if not isinstance(latest, str):
                latest = latest.name
            version = latest
        self._checkout(version)
        yml_contents = []
        for t in self.parse_targets:
            content = self._concat_yaml(t)
            yml_contents.append(content)
        yml_contents = [y for y in yml_contents if y is not None]
        if len(yml_contents) == 0:
            return []
        # Filter `None` to concat all YAMLs
        tasks = yml_contents[0]
        for yml_content in yml_contents[1:]:
            tasks += yml_content
        parsed_tasks = []
        if tasks.content is None:
            logger.warning(f"{self.role_name}: No content")
            return parsed_tasks
        for task in tasks.content:
            parsed = self._parse(task)
            if parsed is None:
                continue
            parsed_tasks.extend(parsed)
        return parsed_tasks


class YAMLFile(object):

    def __init__(self, path: 'Union[str, Path]'):
        self.path = utils.to_path(path)
        self.base_dir = self.path.parent
        if not self.path.exists():
            raise FileNotFoundError(f"'{self.path}' does not exists.")
        with self.path.open('r', encoding='utf-8') as f:
            try:
                self.content = yaml.load(f, Loader=yaml.UnsafeLoader)
            except ParserError as e:
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
