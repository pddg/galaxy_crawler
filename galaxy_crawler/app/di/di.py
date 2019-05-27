from typing import TYPE_CHECKING
from logging import DEBUG, INFO

from galaxy_crawler.store import JsonDataStore
from galaxy_crawler.queries import V1QueryBuilder, QueryOrder
from galaxy_crawler.crawl import Crawler
from galaxy_crawler.logger import enable_file_logger, enable_stream_handler
from galaxy_crawler.utils import to_absolute, mkdir

if TYPE_CHECKING:
    from typing import List
    from queue import Queue
    from galaxy_crawler.app.config import Config
    from galaxy_crawler.repositories import ResponseDataStore
    from galaxy_crawler.queries import QueryBuilder


class AppComponent(object):

    def __init__(self, config: 'Config'):
        self.config = config

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

    def get_crawler(self, url_queue: 'Queue', json_queue: 'Queue') -> 'Crawler':
        return Crawler(
            url_queue=url_queue,
            json_queue=json_queue,
            wait_interval=self.config.interval,
            retry=self.config.retry,
        )

    def get_query_order(self) -> 'QueryOrder':
        order_by = self.config.order_by
        if order_by not in QueryOrder.choices():
            raise ValueError(f"Order type '{order_by}' is not supported.")
        order = QueryOrder[self.config.order_by.upper()]
        return order

    def configure_logger(self) -> None:
        log_level = DEBUG if self.config.debug else INFO
        enable_stream_handler(log_level)
        log_dir = self.config.log_dir
        if log_dir is not None:
            log_file = to_absolute(log_dir)
            mkdir(log_file.parent)
            enable_file_logger(log_dir, log_level)
