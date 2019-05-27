from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Tuple


class QueryOrder(Enum):

    def inverse(self):
        """Descending order"""
        return "-" + self.value

    @classmethod
    def choices(cls):
        choices = tuple(t.name.lower() for t in cls)  # type: Tuple[str]
        return choices


class QueryBuilder(metaclass=ABCMeta):

    @abstractmethod
    def search(self, keyword: 'Optional[str]' = None) -> 'QueryBuilder':
        raise NotImplementedError

    @abstractmethod
    def order_by(self, kind: 'Enum', ascending_order: bool = True) -> 'QueryBuilder':
        raise NotImplementedError

    @abstractmethod
    def build(self):
        raise NotImplementedError

    @abstractmethod
    def join(self, path: str):
        raise NotImplementedError
