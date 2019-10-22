import copy
from typing import TYPE_CHECKING
from urllib import parse

from galaxy_crawler.constants import Target
from .base import QueryBuilder, QueryOrder

if TYPE_CHECKING:
    from typing import Dict, Any

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
            if self.value in [self.NAME, self.CONTRIBUTOR_NAME]:
                return self.value
            return "repository__" + self.value
        return self.value


class V1TargetPath(QueryOrder):
    SEARCH = '/search/content'
    PLATFORMS = '/platforms'
    REPOSITORIES = '/repositories'
    TAGS = '/tags'
    ROLES = '/roles'
    PROVIDERS = '/providers/active'
    NAMESPACES = '/namespaces'
    PROVIDER_NAMESPACES = '/provider_namespaces'
    CONTENT_TYPES = '/content_types'
    IMPORTS = '/imports'

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

    def _replace_path(self, path_name: str) -> 'QueryBuilder':
        suffix = "_path"
        path_name = path_name + suffix
        path = getattr(self, path_name, None)
        if path is None:
            raise AttributeError(f"QueryBuilder has no attribute '{path_name}'")
        if self._path != path:
            self._path = path
        return self

    def order_by(self, kind: 'QueryOrder', ascending_order: bool = False) -> 'QueryBuilder':
        self.ascending_order = ascending_order
        self._queries['order_by'] = kind
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
