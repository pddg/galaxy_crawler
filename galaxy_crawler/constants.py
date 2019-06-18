from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


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
