import logging

from typing import TYPE_CHECKING

from uroboros import ExitStatus, Command

from galaxy_command.commands.tasks import to_dataframe


if TYPE_CHECKING:
    import argparse
    from typing import Union

logger = logging.getLogger(__name__)


class TaskCommand(Command):

    name = 'task'
    short_description = 'Commands related on tasks of Ansible'

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        self.print_help()
        return ExitStatus.SUCCESS


command = TaskCommand()
command.add_command(
    to_dataframe.command
)
