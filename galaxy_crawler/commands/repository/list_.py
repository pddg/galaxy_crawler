import logging
from pathlib import Path
from typing import TYPE_CHECKING

import uroboros
from uroboros.constants import ExitStatus

from galaxy_crawler.ghq import GHQ

if TYPE_CHECKING:
    import argparse
    from typing import Union

logger = logging.getLogger(__name__)


class CloneCommand(uroboros.Command):
    name = 'list'
    short_description = 'List all cloned repositories'
    long_description = 'List all cloned repositories'

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument("output_dir",
                            type=Path,
                            help="Path to clone")
        parser.add_argument("-p",
                            "--full-path",
                            action="store_true",
                            default=False,
                            help="Show full path")
        parser.add_argument("-c",
                            "--count-only",
                            action="store_true",
                            default=False,
                            help="Show only the number of repositories")
        return parser

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        ghq_bin_path = Path('./bin/ghq').expanduser().resolve()
        ghq = GHQ(ghq_bin_path, args.output_dir)
        if args.full_path:
            ghq.set_options(ghq.LIST_CMD, ["-p"])
        else:
            ghq.set_options(ghq.LIST_CMD, [])
        try:
            repositories = ghq.list()
            if args.count_only:
                logger.info(f"{len(repositories)} repositories are cloned in {args.output_dir}")
            else:
                for repo in repositories:
                    logger.info(repo)
        except KeyboardInterrupt:
            return ExitStatus.FAILURE
        return ExitStatus.SUCCESS


command = CloneCommand()
