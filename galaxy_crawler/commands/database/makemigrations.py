import logging
from typing import TYPE_CHECKING

import uroboros
from uroboros.constants import ExitStatus

from .options import StorageOption

if TYPE_CHECKING:
    import argparse
    from typing import Union
    from galaxy_crawler.app.di import AppComponent

logger = logging.getLogger(__name__)


class MakeMigrateCommand(uroboros.Command):

    name = 'makemigrations'
    short_description = 'Generate schema migration script'
    long_description = 'Generate schema migration script based on model definitions and existing database.'
    options = [StorageOption()]

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument('-m', '--message', type=str, help="Revision message")
        return parser

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        c = args.components  # type: AppComponent
        store_cls = c.get_rdb_store_class()
        logger.info("Generate migration scripts")
        try:
            store_cls.makemigrations(
                c.config.kwargs.get("message"),
                c.get_engine()
            )
        except Exception as e:
            logger.error(e)
            return ExitStatus.FAILURE
        return ExitStatus.SUCCESS


command = MakeMigrateCommand()
