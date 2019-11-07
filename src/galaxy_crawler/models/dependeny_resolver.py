import json
import time
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING
from urllib import parse

import requests

from galaxy_crawler.constants import Target
from galaxy_crawler.models import v1 as models
from galaxy_crawler.models.utils import get_role_name_from_json

if TYPE_CHECKING:
    from typing import List, Dict, Any, Optional
    from galaxy_crawler.models.v1 import BaseModel
    from galaxy_crawler.queries import QueryBuilder

logger = getLogger(__name__)


class RoleNotFound(Exception):

    def __init__(self, role_name: str, role_id: 'Optional[int]'):
        self.role_name = role_name
        self.role_id = role_id

    def __str__(self):
        return f"{self.role_name} (id={self.role_id}) was not found"


def _gen_depends(from_id: int, depends: 'List[int]') -> 'List[BaseModel]':
    return [models.RoleDependency(from_id=from_id, to_id=d) for d in depends]


class DependencyResolver(object):
    """Resolve dependencies among role"""
    base_headers = {"content-type": "application/json"}
    map_file_name = 'role_id_mapping.json'

    def __init__(self, query_builder: 'QueryBuilder', interval: int = 5):
        self.query_builder = query_builder
        self.query_builder.clear_query()
        self.base_url = self.query_builder.build(Target.ROLES)
        self.interval = interval
        self.mapped_file = None  # type: Optional[Path]
        self.id_mappings = dict()  # type: Dict[str, int]
        self.dependency_mappings = dict()  # type: Dict[int, List[int]]

    def resolve(self, roles: 'List[Dict[str, Any]]'):
        # Collect role ids and create dict by role name
        self._gen_initial_mappings(roles)
        # Find dependencies
        to_resolve = []
        for r in roles:
            is_resolved = self._resolve_each(r, get_depends_if_fail=True)
            if not is_resolved:
                to_resolve.append(r)
        # Retry to resolve
        for r in to_resolve:
            self._resolve_each(r, get_depends_if_fail=False)
        # Save obtained mapping
        self._save_mapping()
        nested_depends = [
            _gen_depends(from_id, depends)
            for from_id, depends in self.dependency_mappings.items()
        ]
        # Flatten nested list
        return sum(nested_depends, [])

    def load_mapping(self, dir_path: 'Path'):
        self.mapped_file = dir_path / self.map_file_name
        if not self.mapped_file.exists():
            return
        logger.debug(f"Load role mappings from {self.mapped_file}")
        with self.mapped_file.open() as f:
            self.id_mappings = json.load(f)

    def _get_role_id_by_name(self, name: str) -> int:
        id_ = self.id_mappings.get(name)
        if id_ is None:
            raise RoleNotFound(name, None)
        return id_

    def _save_mapping(self):
        if self.mapped_file is None:
            return
        logger.debug(f"Save role mappings as {self.mapped_file}")
        with self.mapped_file.open('w') as f:
            json.dump(self.id_mappings, f)

    def _gen_initial_mappings(self, roles: 'List[Dict[str, Any]]'):
        for r in roles:
            role_id = r['id']
            name = get_role_name_from_json(r)
            self.id_mappings[name] = role_id

    def _update_id_mappings(self, roles: 'List[Dict[str, Any]]'):
        for r in roles:
            name = r['name']
            id_ = r['id']
            logger.debug(f"Update mapping => {name}: {id_}")
            self.id_mappings[name] = id_

    def _resolve_each(self, role: 'Dict[str, Any]', get_depends_if_fail: bool = False) -> 'bool':
        role_name = get_role_name_from_json(role)
        from_id = role.get("id")
        depends = role['summary_fields']['dependencies']
        try:
            for d_name in depends:
                d_id = self._get_role_id_by_name(d_name)
                if from_id not in self.dependency_mappings:
                    self.dependency_mappings[from_id] = [d_id]
                else:
                    if d_id not in self.dependency_mappings[from_id]:
                        self.dependency_mappings[from_id].append(d_id)
            return True
        except RoleNotFound as e:
            if get_depends_if_fail:
                logger.warning(f"Try to obtain actual depends of {role_name} (id={from_id}).")
                actual_depends = self._get_depends(from_id)
                self._update_id_mappings(actual_depends)
            else:
                logger.error(e)
            return False

    def _get_depends(self, role_id: int) -> 'List[Dict[str, Any]]':
        to_access = parse.urljoin(self.base_url, str(role_id))
        resp = requests.get(to_access, headers=self.base_headers)
        logger.debug(f"Get {resp.status_code}: {to_access}")
        if resp.status_code > 200:
            raise Exception(f"'{to_access}' return {resp.status_code}")
        data = resp.json()
        self._sleep()
        return data['summary_fields']['dependencies']

    def _sleep(self):
        logger.debug(f"Wait for {self.interval} sec...")
        time.sleep(self.interval)
