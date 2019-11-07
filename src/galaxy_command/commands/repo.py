import logging
from typing import TYPE_CHECKING

import uroboros
from uroboros.constants import ExitStatus

from .repository import clone, list_

if TYPE_CHECKING:
    import argparse
    from typing import Union

logger = logging.getLogger(__name__)


class RepoCommand(uroboros.Command):

    name = 'repo'
    short_description = 'Sub command for Repository'
    long_description = 'Sub command for Ansible Role Repositories'

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        self.print_help()
        return ExitStatus.FAILURE


command = RepoCommand()
command.add_command(
    clone.command,
    list_.command,
)
