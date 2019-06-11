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
    platforms_path = '/platforms'
    tags_path = '/tags'
    cloud_platforms_path = '/cloud_platforms'
    providers_path = '/providers/active'
    namespaces_path = '/namespaces'
    provider_namespaces_path = '/provider_namespaces'
    content_types_path = '/content_types'
    role_types_path = '/role_types'
    imports_path = '/imports'

    default_queries = {
        "deprecated": False,
        "page_size": 100
    }

    def __init__(self, query_order: 'QueryOrder', ascending_order: bool,
                 deprecated: bool = None, page_size: int = None):
        self._queries = self.default_queries
        if deprecated is not None:
            self._queries['deprecated'] = deprecated
        if page_size is not None:
            self._queries['page_size'] = page_size
        self._path = '/'
        self.order = query_order
        self.ascending_order = ascending_order

    def _replace_path(self, path_name: str) -> 'QueryBuilder':
        suffix = "_path"
        path_name = path_name + suffix
        path = getattr(self, path_name, None)
        if path is None:
            raise AttributeError(f"QueryBuilder has no attribute '{path_name}'")
        if self._path != path:
            self._path = path
        return self

    def search(self, keyword: 'Optional[str]' = None) -> 'QueryBuilder':
        if keyword:
            self._queries['keywords'] = parse.quote(keyword)
        return self._replace_path('search')

    def platforms(self) -> 'QueryBuilder':
        return self._replace_path('platforms')

    def tags(self) -> 'QueryBuilder':
        return self._replace_path('tags')

    def cloud_platforms(self) -> 'QueryBuilder':
        return self._replace_path('cloud_platforms')

    def providers(self) -> 'QueryBuilder':
        return self._replace_path('providers')

    def namespaces(self) -> 'QueryBuilder':
        return self._replace_path('namespaces')

    def role_types(self) -> 'QueryBuilder':
        return self._replace_path('role_types')

    def imports(self) -> 'QueryBuilder':
        return self._replace_path('imports')

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
