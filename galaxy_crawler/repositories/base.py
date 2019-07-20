from typing import TYPE_CHECKING
from abc import ABCMeta, abstractmethod


if TYPE_CHECKING:
    from typing import Any, List
    from galaxy_crawler.constants import Target


class ResponseDataStore(metaclass=ABCMeta):

    @abstractmethod
    def save(self, target: 'Target', obj: 'Any', commit: bool = False) -> 'Any':
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> 'Any':
        raise NotImplementedError
