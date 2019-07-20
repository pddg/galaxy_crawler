from typing import TYPE_CHECKING
from abc import ABCMeta, abstractmethod


if TYPE_CHECKING:
    from typing import Any, List
    from galaxy_crawler.constants import Target
    from galaxy_crawler.models.v1 import BaseModel


class ResponseDataStore(metaclass=ABCMeta):

    @abstractmethod
    def save(self, target: 'Target', obj: 'Any', commit: bool = False) -> 'Any':
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> 'Any':
        raise NotImplementedError


class RDBStorage(metaclass=ABCMeta):

    @abstractmethod
    def save(self, target: 'Target', obj: 'Any') -> 'List[BaseModel]':
        raise NotImplementedError

    @abstractmethod
    def is_migration_required(self) -> 'bool':
        raise NotImplementedError

    @abstractmethod
    def migrate(self) -> 'None':
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def makemigrations(cls, msg: str, engine = None) -> 'None':
        raise NotImplementedError
