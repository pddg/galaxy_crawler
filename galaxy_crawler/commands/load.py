import logging
from pathlib import Path
from typing import TYPE_CHECKING

import uroboros
from uroboros.constants import ExitStatus

from galaxy_crawler.load import JsonLoader
from galaxy_crawler.utils import to_absolute
from .database.options import StorageOption

if TYPE_CHECKING:
    import argparse
    from typing import Union, List

logger = logging.getLogger(__name__)


class LoadCommand(uroboros.Command):
    name = 'load'
    short_description = 'Role info from JSON to DB'
    long_description = 'Load role information from JSON which obtained ' \
                       'by `crawl` command and insert them into DB. \n' \
                       'NOTE: This command delete the existing tables. You should careful to use.'

    options = [StorageOption()]

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument('json_dir',
                            type=Path,
                            help='Path to dir containing JSON')
        parser.add_argument('--interval',
                            type=int,
                            help='Interval time (sec) to access galaxy.ansible.com')
        return parser

    def before_validate(self, unsafe_args: 'argparse.Namespace') -> 'argparse.Namespace':
        unsafe_args.json_dir = to_absolute(unsafe_args.json_dir)
        return unsafe_args

    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        json_dir = args.json_dir
        if not json_dir.exists():
            return [Exception(f"'{json_dir}' does not exists")]
        return []

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        c = args.components
        try:
            engine = c.get_engine()
            rdb_store = c.get_rdb_store()
            resolver = c.get_dependency_resolver()
        except Exception as e:
            logger.error(e)
            return ExitStatus.FAILURE
        json_loader = JsonLoader(args.json_dir, engine, rdb_store, resolver)
        if json_loader.to_rdb_store():
            return ExitStatus.SUCCESS
        return ExitStatus.FAILURE


command = LoadCommand()
