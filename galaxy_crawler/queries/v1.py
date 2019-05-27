from urllib import parse
from enum import Enum
from typing import TYPE_CHECKING
from .base import QueryBuilder

if TYPE_CHECKING:
    from typing import Optional, Tuple


API_BASE_URL = 'https://galaxy.ansible.com/api/v1'


class QueryOrder(Enum):
    DOWNLOAD = "repository__download_count"
    STAR = "repository__stargazers_count"
    CONTRIBUTOR_NAME = "namespace__name,name"
    RELEVANCE = "relevance"
    FORK = "repository__forks_count"
    WATCHER = "repository__watchers_count"

    @classmethod
    def choices(cls):
        choices = tuple(t.name.lower() for t in cls)  # type: Tuple[str]
        return choices

    def inverse(self):
        """Descending order"""
        return "-" + self.value


class V1QueryBuilder(QueryBuilder):

    search_path = '/search/content'

    def __init__(self, deprecated: bool = False, page_size: int = 100):
        self._queries = {
            "deprecated": deprecated,
            "page_size": page_size
        }
        self._path = '/'

    def search(self, keyword: 'Optional[str]' = None) -> 'QueryBuilder':
        if keyword:
            self._queries['keywords'] = parse.quote(keyword)
        if self._path != self.search_path:
            self._path = self.search_path
        return self

    def order_by(self, kind: 'QueryOrder', ascending_order: bool = True) -> 'QueryBuilder':
        order = kind.value
        if not ascending_order:
            order = '-' + order
        self._queries['order_by'] = order
        return self

    def build(self) -> str:
        query_str = parse.urlencode(self._queries)
        parsed = parse.urlparse(API_BASE_URL)
        path = parsed.path + self._path
        return parse.urlunparse(
            (parsed.scheme, parsed.netloc, path, '', query_str, '')
        )

    def join(self, path: str):
        return parse.urljoin(API_BASE_URL, path)
