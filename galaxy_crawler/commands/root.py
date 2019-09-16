from logging import DEBUG, INFO, getLogger
from typing import TYPE_CHECKING
from pathlib import Path

import uroboros
from uroboros.constants import ExitStatus

from galaxy_crawler import version
from galaxy_crawler.app.config import Config
from galaxy_crawler.app.di import AppComponent
from galaxy_crawler.logger import enable_file_logger, enable_stream_handler
from galaxy_crawler.utils import mkdir

if TYPE_CHECKING:
    import argparse
    from typing import Union


logger = getLogger(__name__)


class RootCommand(uroboros.Command):

    name = "galaxy"
    long_description = "Ansible Galaxy crawler"

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument('--version', action='store_true', default=False, help="Show version")
        log_group = parser.add_argument_group("LOGGING")
        log_group.add_argument("--debug", action="store_true", default=False, help="Enable debug logging")
        log_group.add_argument("--log-dir", type=Path, help="Log output directory")
        return parser

    def before_validate(self, unsafe_args: 'argparse.Namespace') -> 'argparse.Namespace':
        # Configure loggers
        log_level = DEBUG if unsafe_args.debug else INFO
        enable_stream_handler(log_level)
        log_dir = unsafe_args.log_dir
        if log_dir is not None:
            try:
                log_dir = mkdir(log_dir)
            except NotADirectoryError:
                logger.warning(f"{log_dir} is not a directory. Use `./logs/` instead.")
                log_dir = mkdir(Path('./logs/'))
            enable_file_logger(log_dir, log_level)
        return unsafe_args

    def after_validate(self, safe_args: 'argparse.Namespace') -> 'argparse.Namespace':
        config = Config.load(safe_args)
        safe_args.components = AppComponent(config)
        return safe_args

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        if args.version:
            print(f"Galaxy Crawler v{version}")
            return ExitStatus.SUCCESS
        self.print_help()
        return ExitStatus.FAILURE


command = RootCommand()
