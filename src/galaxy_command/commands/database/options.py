from typing import TYPE_CHECKING

import uroboros

from galaxy_crawler.models import engine

if TYPE_CHECKING:
    import argparse
    from typing import List


class StorageOption(uroboros.Option):

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument("--storage", type=str, help="Storage path")
        return parser

    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        if args.storage is None:
            return []
        error = engine.EngineType.validate(args.storage)
        if error is None:
            return []
        return [error]

