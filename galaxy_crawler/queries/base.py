from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple
    from galaxy_crawler.constants import Target


class QueryOrder(Enum):

    def inverse(self, query: str) -> str:
        """Descending order"""
        return "-" + query

    @classmethod
    def choices(cls):
        choices = tuple(t.name.lower() for t in cls)  # type: Tuple[str]
        return choices


class QueryBuilder(metaclass=ABCMeta):

    @abstractmethod
    def order_by(self, kind: 'Enum', ascending_order: bool = True) -> 'QueryBuilder':
        raise NotImplementedError

    @abstractmethod
    def build(self, target: 'Target') -> str:
        raise NotImplementedError

    @abstractmethod
    def join(self, path: str):
        raise NotImplementedError
