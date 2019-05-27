import argparse
import logging
from pathlib import Path

from galaxy_crawler.app.config import Config
from galaxy_crawler.app.di import AppComponent
from galaxy_crawler.queries.v1 import V1QueryOrder
from galaxy_crawler.filters.v1 import V1FilterEnum
from galaxy_crawler.errors import NotSupportedFilterError, InvalidExpressionError
from time import sleep

DEFAULT_INTERVAL = Config.DEFAULT_INTERVAL
DEFAULT_RETRY_COUNT = Config.DEFAULT_RETRY

logger = logging.getLogger(__name__)


def scrape(appconfig: 'Config'):
    components = AppComponent(appconfig)
    components.configure_logger()
    try:
        crawler = components.get_crawler()
        parser = components.get_parser()
    except (NotSupportedFilterError, InvalidExpressionError) as e:
        logger.error(e)
        exit(1)

    # Start to crawl and parse on another thread
    crawler.start()
    parser.start()

    try:
        while parser.is_alive():
            sleep(1)
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


def main():
    parser = argparse.ArgumentParser(description="Ansible Galaxy crawler")

    log_parser = argparse.ArgumentParser(add_help=False)
    log_group = log_parser.add_argument_group("LOGGING")
    log_group.add_argument("--debug", action="store_true", default=False, help="Enable debug logging")
    log_group.add_argument("--log-dir", type=Path, help="Log output directory")

    cmd_parser = parser.add_subparsers()
    start_cmd = cmd_parser.add_parser("start", help="Start crawling", parents=[log_parser])
    start_cmd.add_argument("output_dir", type=Path, help="Path to output")
    start_cmd.add_argument("--version", choices=["v1"], help="The API version of galaxy.ansible.com")
    start_cmd.add_argument("--interval", type=int,
                           help=f"Fetch interval (default={DEFAULT_INTERVAL})")
    start_cmd.add_argument("--retry", type=int,
                           help=f"Number of retrying (default={DEFAULT_RETRY_COUNT})")
    start_cmd.add_argument("--format", choices=["json"], nargs="+", dest='output_format',
                           help=f"Output format (default={Config.DEFAULT_OUTPUT_FORMAT})")
    start_cmd.add_argument("--order-by", choices=V1QueryOrder.choices(),
                           help=f"Query order (default={Config.DEFAULT_ORDER_BY}). It is a descending order by default.")
    start_cmd.add_argument("--inverse", action="store_true",
                           help="If this specified, make the order of query inverse")
    start_cmd.add_argument("--filters", type=str, nargs='*',
                           help=f"Filter expression (e.g. download>500). "
                           f"Available filter types are {V1FilterEnum.choices()}")
    start_cmd.set_defaults(func=scrape)
    args = parser.parse_args()
    try:
        config = Config.load(args)
        args.func(config)
    except (ValueError, NotADirectoryError) as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    main()
