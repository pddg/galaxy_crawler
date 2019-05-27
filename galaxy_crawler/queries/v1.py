from typing import TYPE_CHECKING
from urllib import parse

from .base import QueryBuilder, QueryOrder

if TYPE_CHECKING:
    from typing import Optional

API_BASE_URL = 'https://galaxy.ansible.com/api/v1'


class V1QueryOrder(QueryOrder):
    DOWNLOAD = "repository__download_count"
    STAR = "repository__stargazers_count"
    CONTRIBUTOR_NAME = "namespace__name,name"
    RELEVANCE = "relevance"
    FORK = "repository__forks_count"
    WATCHER = "repository__watchers_count"


class V1QueryBuilder(QueryBuilder):
    search_path = '/search/content'

    def __init__(self, query_order: 'QueryOrder', ascending_order: bool,
                 deprecated: bool = False, page_size: int = 100):
        self._queries = {
            "deprecated": deprecated,
            "page_size": page_size
        }
        self._path = '/'
        self.order = query_order
        self.ascending_order = ascending_order

    def search(self, keyword: 'Optional[str]' = None) -> 'QueryBuilder':
        if keyword:
            self._queries['keywords'] = parse.quote(keyword)
        if self._path != self.search_path:
            self._path = self.search_path
        return self

    def order_by(self, kind: 'QueryOrder', ascending_order: bool = False) -> 'QueryBuilder':
        order = kind.value
        if not ascending_order:
            order = kind.inverse()
        self._queries['order_by'] = order
        return self

    def build(self) -> str:
        if 'order_by' not in self._queries:
            self.order_by(self.order, self.ascending_order)
        query_str = parse.urlencode(self._queries)
        parsed = parse.urlparse(API_BASE_URL)
        path = parsed.path + self._path
        return parse.urlunparse(
            (parsed.scheme, parsed.netloc, path, '', query_str, '')
        )

    def join(self, path: str):
        return parse.urljoin(API_BASE_URL, path)
