from .base import Filter
from typing import TYPE_CHECKING
from logging import getLogger
from .base import FilterEnum
from galaxy_crawler.errors import NotSupportedFilterError
from galaxy_crawler.constants import Target


if TYPE_CHECKING:
    from typing import Union


logger = getLogger(__name__)


class V1FilterEnum(FilterEnum):
    DOWNLOAD = 'download_count'
    STAR = 'stargazers_count'
    FORK = 'forks_count'
    ANSIBLE = 'ansible_version'

    @classmethod
    def by_name(cls, name: str, gt: bool, threshold: 'Union[int, float]') -> 'Filter':
        name = name.lower()
        if name not in cls.choices():
            raise NotSupportedFilterError(name)
        if name == 'ansible':
            filter_instance = AnsibleVersionFilter(threshold)
        else:
            filter_instance = CountFilter(cls[name.upper()].value, threshold)
        return filter_instance if gt else not filter_instance


class CountFilter(Filter):
    """Whether the number over the threshold"""

    def __init__(self, key_name: str, threshold: int):
        self.threshold = threshold
        self.key_name = key_name

    def passed(self, target: 'Target', role: 'dict') -> bool:
        if target not in [Target.ROLES, Target.REPOSITORIES]:
            return True
        try:
            count = role[self.key_name]
        except AttributeError:
            logger.error(f"Failed to parse response. Repository has no attribute '{self.key_name}'.")
            return False
        return count > self.threshold


class AnsibleVersionFilter(Filter):
    """Filter for minimum ansible version"""

    def __init__(self, min_version: float):
        self.min_version = min_version
        self.key_name = 'min_ansible_version'

    def passed(self, target: 'Target', role: 'dict') -> bool:
        if target not in [Target.REPOSITORIES, Target.ROLES]:
            return True
        try:
            min_version_str = role[self.key_name]
        except AttributeError:
            logger.error(f"Failed to parse response. Repository has no attribute '{self.key_name}'.")
            return False
        try:
            # Convert 2.0a1 to 2.0
            min_version = float(min_version_str[:3])
        except ValueError:
            # When failed to parse value as float
            logger.warning(f"Cannot parse min_ansible_version ('{min_version_str}'). Use 0.0 instead.")
            min_version = 0.0
        except TypeError:
            # The value is None
            logger.warning(f"Cannot parse min_ansible_version ('{min_version_str}'). Use 0.0 instead.")
            min_version = 0.0
        return min_version >= self.min_version

