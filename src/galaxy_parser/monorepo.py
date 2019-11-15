import logging
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Union

logger = logging.getLogger(__name__)


class NoSuchRole(Exception):
    """There is no such name role"""

    def __init__(self, role_name: 'str', path: 'Union[str, Path]'):
        self.role_name = role_name
        self.path = path

    def __str__(self):
        return f"There is no role named '{self.role_name}' in '{self.path}'"


class NoMetaData(Exception):
    """The role has no metadata"""
    pass


def _get_meta(role_path: 'Path') -> 'dict':
    """
    Load `meta/main.yml` and return the data
    :param role_path: Path to role
    :return: Metadata dictionary
    """
    meta_file = role_path / 'meta' / 'main.yml'
    if not meta_file.exists():
        meta_file = role_path / 'meta' / 'main.yaml'
        if not meta_file.exists():
            raise NoMetaData(role_path)
    with meta_file.open() as f:
        metadata = yaml.safe_load(f)
    return metadata


class RoleFinder(object):
    """
    Find all roles in a repository which seems like Monorepo structure.
    e.g. https://galaxy.ansible.com/ceph/ceph_ansible
    """

    def __init__(self, repo_path: 'Union[str, Path]'):
        self.repo_path = repo_path
        self.roles_dir = self.repo_path / 'roles'
        self.role_path_map = dict()
        self._is_mapped = False

    def is_monorepo(self) -> bool:
        """
        Whether the repository has `roles` sub directory or not.
        There is no evidence of whether the repository is monorepo or not.
        """
        return self.roles_dir.exists()

    def construct_map(self):
        """
        Search all roles in a subdirectory named `roles` and create mapping of role name and actual path.
        :return: None
        """
        if self._is_mapped:
            return
        if not self.roles_dir.exists():
            self._is_mapped = True
            return
        for d in self.roles_dir.iterdir():
            if d.is_file():
                continue
            try:
                meta = _get_meta(d)
            except NoMetaData:
                logger.debug(f"'{d}' is not a Role.")
                continue
            galaxy_info = meta.get('galaxy_info')
            if galaxy_info is None:
                logger.debug(f"'{d}' is not a Role.")
                continue
            role_name = galaxy_info.get('role_name')
            if role_name is None:
                role_name = d.name
                # ansible-role-xxx becomes xxx in Ansible Galaxy
                if role_name.startswith('ansible-role-'):
                    role_name = role_name.replace('ansible-role-', '')
                self.role_path_map[role_name] = d
            else:
                self.role_path_map[role_name] = d
        self._is_mapped = True

    def is_mapped(self):
        return self._is_mapped

    def find(self, role_name: 'str') -> 'Path':
        """
        Find the actual path of the role.
        If the role does not exists, raise NoSuchRole
        :param role_name: Name of role (without namespace)
        :return: Path to role
        """
        if role_name not in self.role_path_map.keys():
            role_name = role_name.replace('_', '-')
            if role_name not in self.role_path_map.keys():
                raise NoSuchRole(role_name, self.repo_path)
        return self.role_path_map.get(role_name)
