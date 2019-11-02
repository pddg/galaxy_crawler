import json
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy.orm import sessionmaker, scoped_session

if TYPE_CHECKING:
    from typing import List
    from sqlalchemy.orm.session import Session
    from .base import ModelInterfaceMixin

logger = getLogger(__name__)


def update_params(old, new) -> 'ModelInterfaceMixin':
    for key, val in new.__dict__.items():
        if key.startswith('_'):
            continue
        if hasattr(old, key):
            setattr(old, key, val)
    return old


def concat_json(json_dir: 'Path') -> 'List[dict]':
    if not json_dir.exists():
        raise FileNotFoundError(f"{json_dir}: No such directory.")
    json_set = []
    for j in json_dir.glob('*.json'):
        with j.open('r') as fp:
            body = json.load(fp)['json']
        idx = int(j.stem.split('_')[-1])
        tmp = []
        for j in body:
            if isinstance(j, list):
                for _j in j:
                    tmp.append(_j)
            else:
                tmp.append(j)
        json_set.append((idx, tmp))
    # Sort json by its file name
    json_set.sort(key=lambda x: x[0])
    json_set = [j[1] for j in json_set]
    # Flatten nested lists
    return sum(json_set, [])


def get_role_name_from_json(j: 'dict') -> str:
    namespace = j['summary_fields']['namespace']['name']
    role_name = j['name']
    name = f"{namespace}.{role_name}"
    return name


def get_scoped_session(engine) -> 'Session':
    session = sessionmaker(bind=engine)
    return scoped_session(session)
