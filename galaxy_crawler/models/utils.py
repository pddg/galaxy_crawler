import functools
import json
from .errors import JSONParseFailed, DateParseFailed

from typing import TYPE_CHECKING
from logging import getLogger
from datetime import datetime
from pathlib import Path

from pytz import timezone

if TYPE_CHECKING:
    from typing import List, Dict
    from sqlalchemy.orm.session import Session
    from .base import ModelInterfaceMixin

logger = getLogger(__name__)

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
UTC = timezone('UTC')


def commit_if_true(func):
    @functools.wraps(func)
    def _commit(*args, session: 'Session', commit: 'bool', **kwargs):
        try:
            obj = func(*args, session, commit, **kwargs)
            if commit:
                session.commit()
            return obj
        except Exception as e:
            session.rollback()
            logger.exception(e)
    return _commit


def update_params(old, new) -> 'ModelInterfaceMixin':
    for key, val in new.__dict__.items():
        if key.startswith('_'):
            continue
        if hasattr(key, old):
            setattr(old, key, val)
    return old


def to_datetime(d_str: 'str') -> 'datetime':
    try:
        dt_obj = datetime.strptime(d_str, DATETIME_FORMAT)
    except ValueError as e:
        raise DateParseFailed(str(e))
    return dt_obj.astimezone(UTC)


def parse_json(keys: 'List[str]', json_obj: 'dict', model_name: 'str') -> 'dict':
    parsed = dict()
    for key in keys:
        if isinstance(key, dict):
            json_key = key['target']
            parsed_key = key['key']
        else:
            json_key = key
            parsed_key = key
        try:
            value = json_obj[json_key]
        except KeyError:
            raise JSONParseFailed(model_name, json_obj)
        if key in ['created', 'modified']:
            json_obj[parsed_key] = to_datetime(value)
        else:
            json_obj[parsed_key] = value
    return parsed


def concat_json(json_dir: 'Path') -> 'dict':
    if not json_dir.exists():
        raise FileNotFoundError(f"{json_dir}: No such directory.")
    json_set = []
    for j in json_dir.glob('*.json'):
        with j.open('r') as fp:
            body = json.load(fp)['json']
        idx = int(j.name.split('_')[-1])
        json_set.append((idx, body))
    # Sort json by its file name
    json_set.sort(key=lambda x: x[0])
    json_set = [j[1] for j in json_set]
    # Flatten nested lists
    return sum(json_set)


def get_role_name_from_json(j: 'dict') -> str:
    namespace = j['summary_fields']['namespace']['name']
    role_name = j['name']
    name = f"{namespace}.{role_name}"
    return name


def resolve_dependencies(all_roles: 'List[dict]'):
    # Collect role ids and create dict by role name
    role_dict = {}
    for r in all_roles:
        role_id = r['id']
        name = get_role_name_from_json(r)
        role_dict[name] = role_id
    # Find dependencies
    for i in range(len(all_roles)):
        r = all_roles[i]
        depends_ids = []
        depends = r['summary_fields']['dependencies']
        for d_name in depends:
            id_ = role_dict.get(d_name)
            if id_ is None:
                name = get_role_name_from_json(r)
                logger.warning(f"Failed to resolve dependency for {name}: "
                               f"'{d_name}' was not found")
                continue
            depends_ids.append(id_)
        all_roles[i]['summary_fields']['dependencies'] = depends_ids
    return all_roles
