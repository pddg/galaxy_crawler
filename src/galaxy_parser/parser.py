import logging
from typing import TYPE_CHECKING

from . import utils
from .module_parsers import GeneralModuleParser
from .repository import Repository

if TYPE_CHECKING:
    from typing import Union, Dict, Optional, List, Type
    from pathlib import Path

    from .module_parsers import ModuleParser
    from galaxy_crawler.models.v1 import Role

logger = logging.getLogger(__name__)


class TaskParser(object):
    """
    Parse all tasks in a Role. This class is a thread safe.
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
        # Path to the repository
        self._repo_path = self._ghq_root / utils.to_role_path(role.repository.clone_url)
        self.repo = Repository(self._repo_path)
        self.parsers = dict()  # type: Dict[str, Type[ModuleParser]]
        self.role_name = f"{self.role.namespace.name}/{self.role.name}"

    def set_parser(self, *parsers: 'Type[ModuleParser]'):
        for parser in parsers:
            name = parser.name
            self.parsers[name] = parser

    def _log(self, msg: str, level: int = logging.DEBUG):
        logger.log(level, f"{self.role_name}: {msg}")

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
            # Try to parse with general parser if there is no appropriate parser.
            parser = GeneralModuleParser
        try:
            parsed_tasks.append(parser(**task))
        except Exception as e:
            self._log(f"Task parse failed due to '{e}'", logging.ERROR)
        return parsed_tasks

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
        # If the repository is a monorepo, lock the repository to use.
        yml_contents = []
        with self.repo as r:
            r.checkout(version)
            role_name = None
            if r.is_monorepo():
                role_name = self.role.name
            for t in self.parse_targets:
                yaml_content = r.get_yaml(t, role_name)
                yml_contents.append(yaml_content)
        yml_contents = [y for y in yml_contents if y is not None]
        if len(yml_contents) == 0:
            return []
        tasks = yml_contents[0]
        for yml_content in yml_contents[1:]:
            tasks += yml_content
        parsed_tasks = []
        if tasks.content is None:
            self._log(f"{self.role_name}: No content", logging.WARNING)
            return parsed_tasks
        for task in tasks.content:
            parsed = self._parse(task)
            if parsed is None:
                continue
            parsed_tasks.extend(parsed)
        return parsed_tasks
