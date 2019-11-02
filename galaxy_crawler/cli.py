import logging

from galaxy_crawler.commands import root, crawl, db, load, repo

logger = logging.getLogger(__name__)


def main():
    root_cmd = root.command
    root_cmd.add_command(
        crawl.command,
        db.command,
        load.command,
        repo.command,
    )
    return root_cmd.execute()


if __name__ == '__main__':
    exit(main())
