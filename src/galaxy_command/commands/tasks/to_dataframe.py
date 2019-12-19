import csv
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import uroboros
from sqlalchemy.orm import sessionmaker, joinedload
from uroboros import ExitStatus

from galaxy_command.commands.database.options import StorageOption
from galaxy_crawler.models import v1 as models
from galaxy_parser import module_parsers
from galaxy_parser.dataframe import to_dataframe
from galaxy_parser.parser import parse_tasks

if TYPE_CHECKING:
    import argparse
    from typing import Union, List
    from sqlalchemy.orm import Session
    from galaxy_command.app.di import AppComponent

logger = logging.getLogger(__name__)

# TODO: Support dynamic parser
parsers = [
    module_parsers.ScriptModuleParser,
    module_parsers.ShellModuleParser,
    module_parsers.RawModuleParser,
    module_parsers.CommandModuleParser,
]


def _read_csv(repo_list_file: 'Path') -> 'pd.DataFrame':
    repo_csv = pd.read_csv(str(repo_list_file), index_col=[0])
    return repo_csv


def _get_roles(role_ids, engine) -> 'List[models.Role]':
    session = sessionmaker(bind=engine)()  # type: Session
    roles = session.query(models.Role) \
        .filter(models.Role.role_id.in_(role_ids)) \
        .options(
        joinedload(models.Role.repository),
        joinedload(models.Role.versions),
        joinedload(models.Role.namespace)) \
        .all()
    session.close()
    return roles


class ToDataFrameCommand(uroboros.Command):
    name = 'to_dataframe'
    short_description = 'Output all tasks as CSV format'
    long_description = 'Output all tasks (such as shell, command ... etc) as CSV format. Flatten all blocks and tasks.'

    options = [StorageOption()]

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument('-l', '--repo-csv', type=Path, required=True, help='Path to repository list csv')
        parser.add_argument('-o', '--output-dir', type=Path, required=True, help='Path to output dir')
        parser.add_argument('-r', '--repo', type=Path, required=True, help='Path to your GHQ_ROOT')
        return parser

    def before_validate(self, unsafe_args: 'argparse.Namespace') -> 'argparse.Namespace':
        unsafe_args.repo_list = unsafe_args.repo_csv.expanduser().resolve()
        unsafe_args.output_dir = unsafe_args.output_dir.expanduser().resolve()
        unsafe_args.repo = unsafe_args.repo.expanduser().resolve()
        return unsafe_args

    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        errors = []
        repo_list_file = args.repo_csv
        if not repo_list_file.exists():
            errors.append(FileNotFoundError(f"{repo_list_file} does not exist."))
        repo_dir = args.repo
        if not repo_dir.exists():
            errors.append(FileNotFoundError(f"{repo_dir} does not exist."))
        elif repo_dir.is_file():
            errors.append(NotADirectoryError(f"{repo_dir} is not a directory."))
        return errors

    def after_validate(self, safe_args: 'argparse.Namespace') -> 'argparse.Namespace':
        out_dir = safe_args.output_dir
        if not out_dir.exists():
            out_dir.mkdir(parents=True)
        return safe_args

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        c = args.components  # type: AppComponent
        role_csv = _read_csv(args.repo_csv)
        role_ids = role_csv.index.tolist()
        engine = c.get_engine()
        roles = _get_roles(role_ids, engine)
        parsed_tasks = parse_tasks(roles, parsers, args.repo)
        # failed_tasks = [t for t in parsed_tasks if t[1].is_failed()]
        tasks = [t[1] for t in parsed_tasks if not t[1].is_failed()]
        df = to_dataframe(tasks, args.repo)
        df.to_csv(args.output_dir / 'tasks.csv', quoting=csv.QUOTE_NONNUMERIC)
        return ExitStatus.SUCCESS


command = ToDataFrameCommand()
