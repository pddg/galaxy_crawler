from queue import Queue
from typing import TYPE_CHECKING

from galaxy_crawler.crawl import Crawler
from galaxy_crawler.filters import DefaultFilter
from galaxy_crawler.filters.v1 import V1FilterEnum
from galaxy_crawler.models.engine import EngineType
from galaxy_crawler.models.dependeny_resolver import DependencyResolver
from galaxy_crawler.parser import ResponseParser
from galaxy_crawler.queries.v1 import V1QueryBuilder, V1QueryOrder
from galaxy_crawler.store import JsonDataStore, RDBStore
from galaxy_crawler.utils import mkdir

if TYPE_CHECKING:
    from typing import List, Type
    from galaxy_crawler.repositories import ResponseDataStore, RDBStorage
    from galaxy_crawler.queries import QueryBuilder, QueryOrder
    from galaxy_crawler.filters import Filter
    from galaxy_crawler.constants import Target
    from galaxy_command.app.config import Config


class AppComponent(object):

    def __init__(self, config: 'Config'):
        self.config = config
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
        return V1QueryBuilder()

    def get_crawler(self) -> 'Crawler':
        return Crawler(
            targets=self.get_targets(),
            query_builder=self.get_query_builder(),
            order=self.get_query_order(),
            json_queue=self.json_queue,
            wait_interval=self.config.interval,
            retry=self.config.retry,
        )

    def get_parser(self) -> 'ResponseParser':
        return ResponseParser(
            json_queue=self.json_queue,
            data_stores=self.get_response_data_stores(),
            filters=self.get_filters(),
        )

    def get_query_order(self) -> 'QueryOrder':
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

    def get_engine(self):
        url = self.config.storage
        if url is None:
            return EngineType.from_env_var().get_engine()
        et = EngineType.from_url(url)
        return et.get_engine(url)

    def get_rdb_store_class(self) -> 'Type[RDBStorage]':
        return RDBStore

    def get_rdb_store(self) -> 'RDBStorage':
        storage_cls = self.get_rdb_store_class()
        return storage_cls(self.get_engine())

    def get_dependency_resolver(self) -> 'DependencyResolver':
        return DependencyResolver(self.get_query_builder(), int(self.config.interval))
