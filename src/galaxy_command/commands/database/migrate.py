import logging
from typing import TYPE_CHECKING

import uroboros
from uroboros.constants import ExitStatus

from .options import StorageOption

if TYPE_CHECKING:
    import argparse
    from typing import Union
    from galaxy_command.app.di import AppComponent

logger = logging.getLogger(__name__)


class MigrateCommand(uroboros.Command):

    name = 'migrate'
    short_description = 'Update schemas'
    long_description = 'Update table schemas automatically'
    options = [StorageOption()]

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        c = args.components  # type: AppComponent
        try:
            store = c.get_rdb_store()
        except Exception as e:
            logger.error(e)
            return ExitStatus.FAILURE
        if store.is_migration_required():
            logger.info("Migration required")
            try:
                store.migrate()
            except Exception as e:
                logger.exception(e)
                logger.error("Migration failed.")
                return ExitStatus.FAILURE
            logger.info("Migration completed successfully")
        else:
            logger.info("The table schemas are up-to-date.")
        logger.info("Done")
        return ExitStatus.SUCCESS


command = MigrateCommand()
