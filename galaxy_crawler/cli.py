import logging
from time import sleep

from galaxy_crawler.app.config import Config
from galaxy_crawler.app.di import AppComponent
from galaxy_crawler.errors import NotSupportedFilterError, InvalidExpressionError

logger = logging.getLogger(__name__)


def scrape(components: 'AppComponent'):
    try:
        crawler = components.get_crawler()
        parser = components.get_parser()
    except (NotSupportedFilterError, InvalidExpressionError) as e:
        logger.error(e)
        return 1

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
    return 0


def migrate(c: 'AppComponent') -> int:
    try:
        store = c.get_rdb_store()
    except Exception as e:
        logger.error(e)
        return 1
    if store.is_migration_required():
        logger.info("Migration required")
        store.migrate()
    else:
        logger.info("The table schemas are up-to-date.")
    logger.info("Done")
    return 0


def mkmigrate(c: 'AppComponent') -> 'int':
    store_cls = c.get_rdb_store_class()
    logger.info("Generate migration scripts")
    try:
        store_cls.makemigrations(
            c.config.kwargs.get("message"),
            c.get_engine()
        )
    except Exception as e:
        logger.error(e)
        return 1
    return 0


def main():
    parser = Config.get_parser()
    args = parser.parse_args()
    if args.version:
        from galaxy_crawler import version
        print(f'Galaxy Crawler v{version}')
        return 0
    try:
        config = Config.load(args)
        components = AppComponent(config)
        components.configure_logger()
    except (ValueError, NotADirectoryError) as e:
        print(e)
        return 1
    if args.func == 'start':
        return scrape(components)
    elif args.func == 'migrate':
        return migrate(components)
    elif args.func == 'makemigrations':
        return mkmigrate(components)


if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
