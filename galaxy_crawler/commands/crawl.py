import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

import uroboros
from uroboros.constants import ExitStatus

from galaxy_crawler import constants
from galaxy_crawler.errors import NotSupportedFilterError, InvalidExpressionError
from galaxy_crawler.filters.v1 import V1FilterEnum
from galaxy_crawler.queries.v1 import V1QueryOrder

if TYPE_CHECKING:
    import argparse
    from typing import Union
    from galaxy_crawler.app.di import AppComponent

logger = logging.getLogger(__name__)


class CrawlCommand(uroboros.Command):
    name = 'crawl'
    short_description = 'Crawl Ansible Galaxy API'
    long_description = 'Start to crawl Ansible Galaxy API and collect information as JSON.'

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument("output_dir", type=Path, help="Path to output")
        parser.add_argument("--interval", type=int,
                            help=f"Fetch interval (default={constants.DEFAULT_INTERVAL})")
        parser.add_argument("--retry", type=int,
                            help=f"Number of retrying (default={constants.DEFAULT_RETRY})")
        parser.add_argument("--format", choices=["json"], nargs="+", dest='output_format',
                            help=f"Output format (default={constants.DEFAULT_OUTPUT_FORMAT})")
        parser.add_argument("--order-by", choices=V1QueryOrder.choices(),
                            help=f"Query order (default={constants.DEFAULT_ORDER_BY})."
                            f" It is a descending order by default.")
        parser.add_argument("--inverse", action="store_true",
                            help="If this specified, make the order of query inverse")
        parser.add_argument("--filters", type=str, nargs='*',
                            help=f"Filter expression (e.g. download>500). "
                            f"Available filter types are {V1FilterEnum.choices()}")
        return parser

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        components = args.components  # type: AppComponent

        try:
            crawler = components.get_crawler()
            parser = components.get_parser()
        except (NotSupportedFilterError, InvalidExpressionError) as e:
            logger.error(e)
            return ExitStatus.FAILURE

        # Start to crawl and parse on another thread
        crawler.start()
        parser.start()

        try:
            while parser.is_alive():
                if not crawler.is_alive():
                    parser.send_stop_signal()
                    parser.join()
                    break
                time.sleep(1)
            if crawler.is_alive():
                crawler.send_stop_signal()
                crawler.join()
        except KeyboardInterrupt:
            logger.error("SIGTERM received.")
            if parser.is_alive():
                parser.send_stop_signal()
                parser.join()
            if crawler.is_alive():
                crawler.send_stop_signal()
                crawler.join()
            return ExitStatus.FAILURE
        return ExitStatus.SUCCESS


command = CrawlCommand()
