from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

# Default values
DEFAULT_INTERVAL = 10
DEFAULT_RETRY = 3
DEFAULT_DEBUG = False
DEFAULT_OUTPUT_FORMAT = ['json']
DEFAULT_ORDER_BY = "id"
DEFAULT_FILTERS = []
DEFAULT_BACKEND = 'postgres'


class Target(Enum):
    ROLES = 'roles'
    REPOSITORIES = 'repositories'
    PLATFORMS = 'platforms'
    TAGS = 'tags'
    PROVIDERS = 'providers'
    PROVIDER_NAMESPACES = 'provider_namespaces'
    NAMESPACES = 'namespaces'

    @classmethod
    def choices(cls) -> 'List[str]':
        return [s for s in cls]
