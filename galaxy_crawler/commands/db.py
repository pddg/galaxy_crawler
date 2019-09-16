import logging
from typing import TYPE_CHECKING

import uroboros
from uroboros.constants import ExitStatus

from .database import migrate, makemigrations

if TYPE_CHECKING:
    import argparse
    from typing import Union

logger = logging.getLogger(__name__)


class DBCommand(uroboros.Command):

    name = 'db'
    short_description = 'Sub command for DB'
    long_description = 'Sub command for relational database'

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        self.print_help()
        return ExitStatus.FAILURE


command = DBCommand()
command.add_command(
    migrate.command,
    makemigrations.command,
)
