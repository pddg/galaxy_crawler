from typing import TYPE_CHECKING
from abc import ABCMeta, abstractmethod


if TYPE_CHECKING:
    from typing import Any, List
    from galaxy_crawler.constants import Target


class ResponseDataStore(metaclass=ABCMeta):

    @abstractmethod
    def exists(self, key: 'Any') -> bool:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: 'Any') -> 'Any':
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> 'List[Any]':
        raise NotImplementedError

    @abstractmethod
    def save(self, target: 'Target', obj: 'Any', commit: bool = False) -> 'Any':
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> 'Any':
        raise NotImplementedError
