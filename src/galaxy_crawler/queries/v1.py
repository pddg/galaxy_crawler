import copy
from typing import TYPE_CHECKING
from urllib import parse

from galaxy_crawler.constants import Target
from .base import QueryBuilder, QueryOrder

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, Tuple

API_BASE_URL = 'https://galaxy.ansible.com/api/v1'


class V1QueryOrder(QueryOrder):
    DOWNLOAD = "download_count"
    STAR = "stargazers_count"
    NAME = "name"
    ID = "id"
    CONTRIBUTOR_NAME = "namespace__name"
    FORK = "forks_count"
    WATCHER = "watchers_count"

    def by_target(self, target) -> str:
        if target == Target.ROLES:
            if self.value in [self.NAME, self.CONTRIBUTOR_NAME, self.ID]:
                return self.value
            return "repository__" + self.value
        return self.value


class V1TargetPath(QueryOrder):
    SEARCH = '/search/content/'
    PLATFORMS = '/platforms/'
    REPOSITORIES = '/repositories/'
    TAGS = '/tags/'
    ROLES = '/roles/'
    PROVIDERS = '/providers/active'
    NAMESPACES = '/namespaces/'
    PROVIDER_NAMESPACES = '/provider_namespaces/'
    CONTENT_TYPES = '/content_types/'
    IMPORTS = '/imports/'

    @classmethod
    def from_target(cls, t: 'Target'):
        return cls[t.name]


class V1QueryBuilder(QueryBuilder):
    default_queries = {
        "page_size": 100
    }

    def __init__(self, page_size: int = None):
        self._queries = self.default_queries  # type: Dict[Any]
        if page_size is not None:
            self._queries['page_size'] = page_size
        self._default_queries = copy.deepcopy(self._queries)
        self._path = '/'
        self.ascending_order = False

    def order_by(self, kind: 'QueryOrder', ascending_order: bool = True) -> 'QueryBuilder':
        self.ascending_order = ascending_order
        self._queries['order_by'] = kind
        return self

    def set_page(self, page: 'Tuple[int, int]') -> 'QueryBuilder':
        self._queries['page'] = page[0]
        self._queries['page_size'] = page[1]
        return self

    def build(self, target: 'Target') -> str:
        order = self._queries.get('order_by')
        if order is not None:
            order_str = order.by_target(target)
            if not self.ascending_order:
                order_str = order.inverse(order_str)
            self._queries['order_by'] = order_str
        query_str = parse.urlencode(self._queries)
        parsed = parse.urlparse(API_BASE_URL)
        path = parsed.path + V1TargetPath.from_target(target).value
        # Initialize
        self.ascending_order = False
        self._queries = copy.deepcopy(self._default_queries)
        return parse.urlunparse(
            (parsed.scheme, parsed.netloc, path, '', query_str, '')
        )

    def join(self, path: str):
        return parse.urljoin(API_BASE_URL, path)

    def clear_query(self):
        self._queries = {}


class Paginator(object):

    def __init__(self,
                 page_size: int,
                 start: int = 0,
                 end: 'Optional[int]' = None,
                 parent: 'Optional[Paginator]' = None):
        self.start_position = start
        self.end_position = end
        self.page_size = page_size
        self.current_position = start
        self._child = None  # type: Optional[Paginator]
        self._parent = parent  # type: Optional[Paginator]

    def next_page(self) -> 'Tuple[int, int]':
        if self._has_child():
            return self._child.next_page()
        if self.end_position is not None \
                and self.current_position >= self.end_position:
            return self.exit_failed_state()
        if self.current_position % self.page_size == 0:
            n = 1
        else:
            n = 0
        page_count = self.current_position // self.page_size + n
        self._increment()
        return page_count, self.page_size

    def _increment(self):
        self.current_position += self.page_size

    def remove_child(self, current_position: int) -> 'Tuple[int, int]':
        assert self._has_child(), "This paginator has no child."
        self.current_position = current_position
        self._child = None
        return self.next_page()

    def _has_child(self):
        return False if self._child is None else True

    def _has_parent(self):
        return False if self._parent is None else True

    def enter_failed_state(self):
        assert self.page_size != 1, "Not supported operation. page size must be greater than 1."
        if self._has_child():
            self._child.enter_failed_state()
        else:
            page_size = self.page_size // 10
            failed_position = self.current_position - self.page_size
            end_position = failed_position + page_size * 10
            self._child = Paginator(page_size, failed_position, end_position, self)

    def exit_failed_state(self) -> 'Tuple[int, int]':
        return self._parent.remove_child(self.current_position)

    def extract_page_size(self, url_str: str) -> int:
        parsed_url = parse.urlparse(url_str)
        parsed_query = parse.parse_qs(parsed_url.query)
        page_sizes = parsed_query.get('page_size')
        if page_sizes is None:
            raise AttributeError("page_size is not in the query.")
        return int(page_sizes[0])
