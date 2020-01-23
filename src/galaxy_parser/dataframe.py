import logging
import base64
from pathlib import Path

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from typing import List, Optional
    from galaxy_crawler.models.v1 import Role
    from galaxy_parser.module_parsers import BaseCommandModuleParser
    from galaxy_parser.parser import ParserManager

logger = logging.getLogger(__name__)

_headers = ['role_id', 'role_name', 'role_owner', 'role_repository', 'role_version', 'min_ansible_version',
            'module', 'name', 'script', 'yaml', 'is_rescue', 'yaml_path', 'has_when', 'is_handler',
            'has_creates', 'has_removes', 'changed_when', 'failed_when', 'published_at']


def _make_row(task: 'BaseCommandModuleParser', role: 'Role', version: str, is_rescue: bool, ghq_root: 'Optional[Path]'):
    # To keep the structure of YAML in CSV file format, convert it to BASE64 string.
    yml = task.as_yaml()
    yml_b64 = base64.b64encode(yml.encode('utf-8')).decode('utf-8')
    pub_date = ''
    if len(role.versions) == 0:
        pub_date = role.repository.modified
    else:
        for v in role.versions:
            if v.name == version:
                pub_date = v.release_date
    # Obtain relative path
    yml_path = Path(task._file)
    if ghq_root is not None:
        yml_path = yml_path.relative_to(ghq_root)
    has_creates = True if len(task.args.get('creates', "")) != 0 else False
    has_removes = True if len(task.args.get('removes', "")) != 0 else False
    return [
        role.role_id, role.name, role.namespace.name, role.repository.clone_url, version, role.min_ansible_version,
        task.name, task._kwargs.get('name', 'No name'), task.command, yml_b64, is_rescue, yml_path, task.has_when(),
        task.is_handler(), has_creates, has_removes, task.changed_when,
        task.failed_when, pub_date
    ]


def to_dataframe(parsed_tasks: 'List[ParserManager]', ghq_root: 'Optional[Path]' = None) -> 'pd.DataFrame':
    regular_tasks = sum([[(r, p.role, p.role_version, False) for r in p.get_tasks()] for p in parsed_tasks], [])
    rescue_tasks = sum([[(r, p.role, p.role_version, True) for r in p.get_rescue_tasks()] for p in parsed_tasks], [])
    all_tasks = regular_tasks + rescue_tasks
    # Filtering all general modules
    rows = [_make_row(*t, ghq_root) for t in all_tasks if t[0].name is not None]
    df = pd.DataFrame(data=rows, columns=_headers)
    df.set_index('role_id', drop=True, inplace=True)
    return df
