import os
import re
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy.engine import create_engine

from galaxy_crawler.constants import (
    ENV_VARS_PREFIX,
    DEFAULT_DB_HOST,
    DEFAULT_DB_TYPE,
    DEFAULT_DB_PORT,
    DEFAULT_DB_NAME,
    DEFAULT_DB_PATH,
    DEFAULT_DB_USER,
    DEFAULT_DB_PASSWORD,
)
from .errors import InsufficientParameter, InvalidParameter

if TYPE_CHECKING:
    from typing import Optional, Union, List
    from sqlalchemy.engine import Engine

_default_db_info = {
    'type': DEFAULT_DB_TYPE,
    'host': DEFAULT_DB_HOST,
    'port': DEFAULT_DB_PORT,
    'name': DEFAULT_DB_NAME,
    'path': DEFAULT_DB_PATH,
    'user': DEFAULT_DB_USER,
    'password': DEFAULT_DB_PASSWORD,
}


def get_in_memory_database() -> 'Engine':
    return create_engine("sqlite://")


def _check_params(param_keys: 'List[str]', local_vars: 'dict'):
    for key in param_keys:
        v = local_vars.get(key)
        if v is None:
            raise InsufficientParameter(key, ENV_VARS_PREFIX + "_DB")


def get_postgres_url(host: 'Optional[str]' = None,
                     port: 'Optional[Union[str, int]]' = None,
                     name: 'Optional[str]' = None,
                     user: 'Optional[str]' = None,
                     password: 'Optional[str]' = None, **kwargs) -> str:
    """
    Get PostgreSQL database URL for creating connection
    :param host: Hostname of PostgreSQL host
    :param port: Port number to connect it
    :param name: Name of database in it
    :param user: User name to connect
    :param password: Password of the user
    :return: postgresql://{user}:{password}@{host}:{port}/{name}
    """
    _check_params(['host', 'port', 'name', 'user', 'password'], locals())
    return f"postgresql://{user}:{password}@{host}:{str(port)}/{name}"


def get_mysql_url(host: 'Optional[str]' = None,
                  port: 'Optional[Union[str, int]]' = None,
                  name: 'Optional[str]' = None,
                  user: 'Optional[str]' = None,
                  password: 'Optional[str]' = None, **kwargs) -> str:
    """
    Get MySQL database URL for creating connection
    :param host: Hostname of MySQL host
    :param port: Port number to connect it
    :param name: Name of database in it
    :param user: User name to connect
    :param password: Password of the user
    :return: mysql+pymysql://{user}:{password}@{host}:{port}/{name}
    """
    _check_params(['host', 'port', 'name', 'user', 'password'], locals())
    return f"mysql+pymysql://{user}:{password}@{host}:{str(port)}/{name}"


def get_sqlite_url(path: 'Optional[str]' = None, **kwargs) -> str:
    """
    Get SQLite3 url for creating connection
    :param path: Path to sqlite3 database file
    :return: sqlite3:///{path}
    """
    _check_params(['path'], locals())
    path = Path(path).expanduser().resolve()
    return f"sqlite3:///{path}"


def get_in_memory_url(**kwargs) -> str:
    return "sqlite://"


class InvalidUrlError(Exception):

    def __init__(self, url: str, backend: str):
        self.url = url
        self.backend = backend.lower()

    def __str__(self):
        return f"'{self.url}' is invalid for the backend ({self.backend})"


class EngineType(Enum):
    IN_MEMORY = r'^sqlite://$'
    POSTGRES = r'^postgresql\:\/\/([^\/]+(\:[^\/]+)?@)?[^\/]+\:[0-9]+\/.+$'
    MYSQL = r'^mysql+pymysql\:\/\/([^\/]+(\:[^\/]+)?@)?[^\/]+\:[0-9]+\/.+$'
    SQLITE = r'^sqlite\:\/\/\/\/?.+$'

    @classmethod
    def validate(cls, url: str) -> 'Optional[Exception]':
        for c in cls:
            reg = re.compile(c.value)
            if reg.match(url):
                return None
        return InvalidUrlError(url, "not specified")

    @classmethod
    def from_url(cls, url: str):
        for c in cls:
            reg = re.compile(c.value)
            if reg.match(url):
                return cls[c.name]
        raise InvalidUrlError(url, "not specified")

    @classmethod
    def from_env_var(cls, envs: 'Optional[dict]' = None):
        if envs is None:
            envs = os.environ
        params = {}
        for key, val in _default_db_info.items():
            var_key = ENV_VARS_PREFIX + f"_DB_{key.upper()}"
            params[var_key] = envs.get(var_key, val)
        db_type = params.get(ENV_VARS_PREFIX + f"_DB_TYPE")
        if db_type is None:
            raise InsufficientParameter('type', ENV_VARS_PREFIX + '_DB')
        db_type = db_type.lower()
        if db_type not in cls.choices():
            raise InvalidParameter('DB_TYPE', f"One of {cls.choices()}")
        return cls[db_type.upper()]

    def get_engine_from_env(self, envs: 'Optional[dict]' = None) -> 'Engine':
        if envs is None:
            envs = os.environ
        params = {}
        for key in _default_db_info.keys():
            params[key] = envs.get(ENV_VARS_PREFIX + f"_DB_{key.upper()}", _default_db_info.get(key))
        get_engine_func = globals().get(f"get_{self.name.lower()}_url")
        url = get_engine_func(**params)
        return self.get_engine(url)

    def get_engine(self, url: 'Optional[str]' = None) -> 'Engine':
        reg = re.compile(self.value)
        if url is None:
            return self.get_engine_from_env()
        if reg.match(url):
            engine = create_engine(url)
        else:
            raise InvalidUrlError(url, self.name)
        return engine

    @classmethod
    def choices(cls):
        return tuple(c.name.lower() for c in cls)
