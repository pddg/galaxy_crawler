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

DEFAULT_DB_TYPE = 'postgres'
DEFAULT_DB_HOST = '127.0.0.1'
DEFAULT_DB_PORT = '5432'
DEFAULT_DB_NAME = 'galaxy'
DEFAULT_DB_USER = 'galaxy'
DEFAULT_DB_PASSWORD = 'galaxy'
DEFAULT_DB_PATH = 'sqlite3.db'

# Prefix of environment variables
ENV_VARS_PREFIX = "GALAXY"


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
