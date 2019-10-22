import logging
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy.orm import sessionmaker
import uroboros
from uroboros.constants import ExitStatus

from galaxy_crawler.utils import to_absolute
from galaxy_crawler.models.utils import concat_json, resolve_dependencies
from galaxy_crawler.models import v1 as models
from .database.options import StorageOption

if TYPE_CHECKING:
    import argparse
    from typing import Union, List

logger = logging.getLogger(__name__)


def insert(json_obj: dict, model: 'models.BaseModel', session) -> 'bool':
    try:
        model.from_json(json_obj, session)
        session.commit()
    except Exception as e:
        logger.warning(f"Insert obj (id={json_obj['id']}) failed due to {e.__class__.__name__}.")
        logger.warning(str(e))
        session.rollback()
        return False
    return True


def insert_dependencies(json_objs, session: 'models.Session'):
    logger.info("Try to resolve role dependencies.")
    resolve_fails = []
    objs = json_objs
    while len(objs) > 0:
        for j in objs:
            ok = models.Role.resolve_dependencies(j, session)
            if not ok:
                resolve_fails.append(j)
            else:
                if j in resolve_fails:
                    resolve_fails.remove(j)
        session.commit()
        objs = resolve_fails


class LoadCommand(uroboros.Command):

    name = 'load'
    short_description = 'Role info from JSON to DB'
    long_description = 'Load role information from JSON which obtained by `crawl` command and insert them into DB.'

    options = [StorageOption()]

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument('json_dir', type=Path, help='Path to dir containing JSON')
        return parser

    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        json_dir = to_absolute(args.json_dir)
        if not json_dir.exists():
            return [Exception(f"'{json_dir}' does not exists")]
        return []

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        c = args.components
        try:
            engine = c.get_engine()
        except Exception as e:
            logger.error(e)
            return ExitStatus.FAILURE
        session = sessionmaker(bind=engine, autocommit=False)()
        json_dir = to_absolute(args.json_dir)
        targets = {
            'providers': models.Provider,
            'platforms': models.Platform,
            'tags': models.Tag,
            'namespaces': models.Namespace,
            'provider_namespaces': models.ProviderNamespace,
            'repositories': models.Repository,
            'roles': models.Role,
        }
        for name, model in targets.items():
            json_objs = concat_json(json_dir / name)
            logger.info(f"{name}: {len(json_objs)} objects were found")
            if name == 'roles':
                json_objs = resolve_dependencies(json_objs)
            try:
                for j in json_objs:
                    insert(j, model, session)
                if name == 'roles':
                    insert_dependencies(json_objs, session)
            except Exception as e:
                logger.exception(str(e))
                session.rollback()
                logger.error("Rollback.")
                return ExitStatus.FAILURE
        logger.info("Done")
        return ExitStatus.SUCCESS


command = LoadCommand()
