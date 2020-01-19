import functools
import logging
import pickle
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import fasteners
from git.exc import NoSuchPathError

from . import utils
from .errors import NoTasks, RepositoryNotFound
from .module_parsers import Block
from .repository import Repository, YAMLFile

if TYPE_CHECKING:
    from typing import Union, Dict, Optional, List, Type, Tuple

    from .module_parsers import ModuleParser
    from galaxy_crawler.models.v1 import Role

logger = logging.getLogger(__name__)


class ParserManager(object):
    """
    Manager object for ModuleParser
    """

    def __init__(self,
                 role: 'Role',
                 repo_path: Path,
                 yaml_contents: 'Dict[str, YAMLFile]',
                 parsers: 'Dict[str, Type[ModuleParser]]',
                 role_version: str):
        self.role = role
        self.repo_path = repo_path
        self.parsers = parsers
        self._yaml_contents = yaml_contents
        self.role_version = role_version
        self.exception = None  # type: Optional[Exception]
        try:
            self._contents = {
                path: self._block_from_contents(str(path), content)
                for path, content in yaml_contents.items()
            }
        except Exception as e:
            self.exception = e
        if len(self.get_blocks()) == 0:
            self.exception = NoTasks(self.role.get_role_name(), self.repo_path)

    def _block_from_contents(self, filepath: str, content: 'YAMLFile') -> 'List[Block]':
        blocks = []
        for block in content.content:
            b = Block(**block)
            b.set_file(filepath)
            b.parse(self.parsers)
            if content.is_handler:
                b.set_as_handler()
            blocks.append(b)
        return blocks

    def is_failed(self) -> 'bool':
        if self.exception is None:
            return False
        return True

    def get_blocks(self) -> 'List[Block]':
        all_blocks = sum(self._contents.values(), [])
        return all_blocks

    def _get_flatten(self, target) -> 'List[ModuleParser]':
        all_blocks = self.get_blocks()
        tasks = []
        for block in all_blocks:
            get_func = getattr(block, f'get_{target}_tasks_flatten', block.get_tasks_flatten)
            tasks.extend(get_func())
        return tasks

    def get_tasks(self) -> 'List[ModuleParser]':
        return self._get_flatten('regular')

    def get_rescue_tasks(self) -> 'List[ModuleParser]':
        return self._get_flatten('rescue')

    def get_all_tasks(self) -> 'List[ModuleParser]':
        return self._get_flatten('all')

    def dump(self, dump_file_path: 'Path'):
        with dump_file_path.open('wb') as dump_file:
            pickle.dump(self, dump_file)

    @classmethod
    def load(cls, dump_file_path: 'Path') -> 'ParserManager':
        if not dump_file_path.exists():
            raise FileNotFoundError(f"'{dump_file_path}' does not exist.")
        with dump_file_path.open('rb') as dump_file:
            manager = pickle.load(dump_file)
        return manager

    @classmethod
    def from_exception(cls, role, repo_path, exc: 'Exception', role_version: 'Optional[str]' = None) -> 'ParserManager':
        m = ParserManager(role, repo_path, {}, {}, role_version if role_version else '')
        m.exception = exc
        return m


class TaskParser(object):
    """
    Parse all tasks in a Role. This class is a thread safe.
    """
    parse_targets = [
        'tasks',
        'handlers'
    ]
    dump_dir_name = 'parsed_tasks'

    def __init__(self, role: 'Role', ghq_root: 'Union[str, Path]'):
        self.role = role
        self.role_name = role.get_role_name()
        self._ghq_root = utils.to_path(ghq_root)
        # Path to the repository
        self._repo_path = self._ghq_root / utils.to_role_path(role.repository.clone_url)
        try:
            self.repo = Repository(self._repo_path)
        except NoSuchPathError:
            raise RepositoryNotFound(self._repo_path)
        self.parsers = dict()  # type: Dict[str, Type[ModuleParser]]

    def set_parser(self, *parsers: 'Type[ModuleParser]'):
        for parser in parsers:
            name = parser.name
            self.parsers[name] = parser

    def _log(self, msg: str, level: int = logging.DEBUG):
        logger.log(level, f"{self.role_name}: {msg}")

    def parse(self, version: 'Optional[str]' = None) -> 'Optional[ParserManager]':
        """
        Parse all YAML file in Role. Parse by given ModuleParser.
        :param version: Branch or tag, commit hash to checkout
        :return: Parsed modules
        """
        if version is None:
            version = self._get_stable_version()
        dump_file = self._get_dump_file(version)
        try:
            exists = ParserManager.load(dump_file)
            return exists
        except FileNotFoundError:
            pass
        # If the repository is a monorepo, checkout will be conflict.
        # Lock the repository before using.
        files = dict()
        try:
            self.repo.checkout(version)
            role_name = None
            if self.repo.is_monorepo():
                role_name = self.role.name
            for t in self.parse_targets:
                files.update(self.repo.get_yaml(t, role_name))
            if len(files) == 0:
                raise NoTasks(self.role_name, self.repo.path)
        except Exception as e:
            return ParserManager.from_exception(self.role, self._repo_path, e)
        finally:
            self.repo.cleanup()
        manager = ParserManager(self.role, self._repo_path, files, self.parsers, version)
        # Save obtained tasks
        manager.dump(dump_file)
        return manager

    def _get_stable_version(self):
        # Checkout latest release
        latest = self.role.get_stable_version()
        if not isinstance(latest, str):
            latest = latest.name
        return latest

    def _get_dump_dir(self) -> 'Path':
        dump_dir = self._ghq_root.parent / self.dump_dir_name
        if not dump_dir.exists():
            dump_dir.mkdir(parents=True)
        return dump_dir

    @functools.lru_cache()
    def _get_dump_file(self, version: str) -> 'Path':
        dump_dir = self._get_dump_dir()
        dump_file = dump_dir / utils.get_dump_name(self.role_name, version)
        return dump_file

    def load(self, version: 'Optional[str]' = None) -> 'Optional[ParserManager]':
        if version is None:
            version = self._get_stable_version()
        dump_file = self._get_dump_file(version)
        return ParserManager.load(dump_file)

    def clean(self):
        """
        Delete all dump files
        :return: None
        """
        dump_dir = self._get_dump_dir()
        for f in dump_dir.glob('**/*.pickle'):
            f.unlink()


def _parse(role: 'Role',
           parsers: 'List[Type[ModuleParser]]',
           ghq_root: 'Path',
           temp_dir: 'Path') -> 'Tuple[str, Optional[ParserManager]]':
    role_name = f'{role.namespace.name}/{role.name}'
    lock_file = temp_dir / str(role.repository.repository_id)
    with fasteners.InterProcessLock(str(lock_file)):
        try:
            task_parser = TaskParser(role, ghq_root)
            task_parser.set_parser(*parsers)
            parsed_task = task_parser.parse()
        except Exception as e:
            return role, ParserManager.from_exception(role, None, e)
        return role, parsed_task


def parse_tasks(roles: 'List[Role]',
                parsers: 'List[Type[ModuleParser]]',
                root_dir: 'Union[str, Path]',
                temp_dir: 'Optional[Union[str, Path, tempfile.TemporaryDirectory]]' = None,
                n_jobs: int = -1):
    """
    Parse all tasks in the roles.
    Return the dictionary that used role name as key and the parsed tasks as value.
    If the parsing is failed, the result will become `None`.
    :param roles: Ansible Role list to use.
    :param parsers: List of ModuleParses class to use
    :param root_dir: Root directory of cloned repositories
    :param temp_dir: Temporary directory to use
    :param n_jobs: Number of process to use
    :return: {models.v1.Role(): ParserManager(), ...]}, {models.v1.Role(): None}
    """
    root_dir = utils.to_path(root_dir)
    assert root_dir.exists(), f"'{root_dir}' does not exists."
    if isinstance(temp_dir, str) or isinstance(temp_dir, Path):
        temp_dir = tempfile.TemporaryDirectory(dir=str(temp_dir))
    elif temp_dir is None:
        temp_dir = tempfile.TemporaryDirectory()
    with temp_dir as tmp:
        parse_func = functools.partial(_parse,
                                       parsers=parsers,
                                       ghq_root=root_dir,
                                       temp_dir=Path(tmp))
        parsed_tasks = utils.parallel(parse_func, roles, n_jobs)
    return parsed_tasks
