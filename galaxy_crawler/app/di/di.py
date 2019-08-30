from logging import DEBUG, INFO
from queue import Queue
from typing import TYPE_CHECKING

from galaxy_crawler.crawl import Crawler
from galaxy_crawler.filters import DefaultFilter
from galaxy_crawler.filters.v1 import V1FilterEnum
from galaxy_crawler.logger import enable_file_logger, enable_stream_handler
from galaxy_crawler.parser import ResponseParser
from galaxy_crawler.queries.v1 import V1QueryBuilder, V1QueryOrder
from galaxy_crawler.store import JsonDataStore, RDBStore
from galaxy_crawler.utils import to_absolute, mkdir
from galaxy_crawler.models.engine import EngineType

if TYPE_CHECKING:
    from typing import List, Type
    from galaxy_crawler.app.config import Config
    from galaxy_crawler.repositories import ResponseDataStore, RDBStorage
    from galaxy_crawler.queries import QueryBuilder, QueryOrder
    from galaxy_crawler.filters import Filter
    from galaxy_crawler.constants import Target


class AppComponent(object):

    def __init__(self, config: 'Config'):
        self.config = config
        self.url_queue = Queue()
        self.json_queue = Queue()

    def get_response_data_stores(self) -> 'List[ResponseDataStore]':
        output_dir = self.config.output_dir
        stores = list()
        mkdir(output_dir)
        for store_format in self.config.output_format:
            if store_format == "json":
                stores.append(JsonDataStore(output_dir))
        assert len(stores) != 0, "No data format specified"
        return stores

    def get_query_builder(self) -> 'QueryBuilder':
        assert self.config.version == "v1", f"Specified version '{self.config.version}' is not supported."
        return V1QueryBuilder()

    def get_crawler(self) -> 'Crawler':
        return Crawler(
            url_queue=self.url_queue,
            json_queue=self.json_queue,
            wait_interval=self.config.interval,
            retry=self.config.retry,
        )

    def get_parser(self) -> 'ResponseParser':
        return ResponseParser(
            url_queue=self.url_queue,
            json_queue=self.json_queue,
            data_stores=self.get_response_data_stores(),
            query_builder=self.get_query_builder(),
            filters=self.get_filters(),
            targets=self.get_targets(),
            order=self.get_query_order()
        )

    def get_query_order(self) -> 'QueryOrder':
        assert self.config.version == "v1", f"Specified version '{self.config.version}' is not supported."
        order_by = self.config.order_by
        if order_by not in V1QueryOrder.choices():
            raise ValueError(f"Order type '{order_by}' is not supported.")
        order = V1QueryOrder[self.config.order_by.upper()]
        return order

    def get_filters(self) -> 'List[Filter]':
        filters = self.config.filters
        if len(filters) == 0:
            return [DefaultFilter()]
        return [V1FilterEnum.by_expr(f) for f in filters]

    def get_targets(self) -> 'List[Target]':
        return self.config.targets

    def configure_logger(self) -> None:
        log_level = DEBUG if self.config.debug else INFO
        enable_stream_handler(log_level)
        log_dir = self.config.log_dir
        if log_dir is not None:
            log_file = to_absolute(log_dir)
            mkdir(log_file.parent)
            enable_file_logger(log_dir, log_level)

    def get_engine(self):
        url = self.config.storage
        et = EngineType.from_url(url)
        return et.get_engine(url)

    def get_rdb_store_class(self) -> 'Type[RDBStorage]':
        return RDBStore

    def get_rdb_store(self) -> 'RDBStorage':
        storage_cls = self.get_rdb_store_class()
        return storage_cls(self.get_engine())
