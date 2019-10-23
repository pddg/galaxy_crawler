import logging
from pathlib import Path
from typing import TYPE_CHECKING

import uroboros
from sqlalchemy.orm import sessionmaker
from uroboros.constants import ExitStatus

from galaxy_crawler.models import v1 as models
from galaxy_crawler.models.utils import concat_json
from galaxy_crawler.utils import to_absolute
from .database.options import StorageOption

if TYPE_CHECKING:
    import argparse
    from typing import Union, List

logger = logging.getLogger(__name__)


def insert(json_obj: dict, model: 'models.BaseModel', session: 'models.Session'):
    try:
        return model.from_json(json_obj, session)
    except Exception as e:
        logger.warning(f"Insert obj (id={json_obj['id']}) failed due to {e.__class__.__name__}.")
        logger.exception(str(e))
        return None


class LoadCommand(uroboros.Command):
    name = 'load'
    short_description = 'Role info from JSON to DB'
    long_description = 'Load role information from JSON which obtained by `crawl` command and insert them into DB.'

    options = [StorageOption()]

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument('json_dir', type=Path, help='Path to dir containing JSON')
        parser.add_argument('--interval', type=int, help='Path to dir containing JSON')
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
            rdb_store = c.get_rdb_store()
            resolver = c.get_dependency_resolver()
            logger.debug("Drop existing tables")
            rdb_store.drop_tables()
            logger.debug("Create tables")
            rdb_store.create_tables()
        except Exception as e:
            logger.error(e)
            return ExitStatus.FAILURE
        session = sessionmaker(bind=engine, autocommit=False)()  # type: models.Session
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
            try:
                objs = []
                for j in json_objs:
                    obj = insert(j, model, session)
                    if obj is not None:
                        objs.append(obj)
                session.add_all(objs)
                if name == 'roles':
                    logger.info("Try to resolve role dependencies.")
                    depends = resolver.resolve(json_objs)
                    session.add_all(depends)
                session.commit()
            except Exception as e:
                logger.exception(str(e))
                session.rollback()
                logger.error("Rollback.")
                return ExitStatus.FAILURE
        logger.info("Done")
        return ExitStatus.SUCCESS


command = LoadCommand()
