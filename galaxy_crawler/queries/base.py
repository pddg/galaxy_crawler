from typing import TYPE_CHECKING
from abc import ABCMeta, abstractmethod

if TYPE_CHECKING:
    from typing import Optional
    from enum import Enum


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
