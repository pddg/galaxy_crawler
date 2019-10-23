import logging

from sqlalchemy.orm import sessionmaker

from galaxy_crawler.models.utils import concat_json
from galaxy_crawler.models import v1 as models

logger = logging.getLogger(__name__)


def insert(json_obj: dict, model: 'models.BaseModel', session: 'models.Session'):
    try:
        return model.from_json(json_obj, session)
    except Exception as e:
        logger.warning(f"Insert obj (id={json_obj['id']}) failed due to {e.__class__.__name__}.")
        logger.exception(str(e))
        return None


class JsonLoader(object):
    """Load JSON and insert them to RDB"""

    def __init__(self, json_dir, engine, rdb_store, resolver):
        self.json_dir = json_dir
        self.engine = engine
        self.rdb_store = rdb_store
        self.resolver = resolver

    def _initialize(self) -> bool:
        """Delete existing tables"""
        try:
            logger.debug("Drop existing tables")
            self.rdb_store.drop_tables()
            logger.debug("Create tables")
            self.rdb_store.create_tables()
        except Exception as e:
            logger.error(e)
            return False
        return True

    def get_session(self) -> 'models.Session':
        return sessionmaker(bind=self.engine, autocommit=False)()

    def to_rdb_store(self) -> bool:
        if not self._initialize():
            return False
        targets = {
            'providers': models.Provider,
            'platforms': models.Platform,
            'tags': models.Tag,
            'namespaces': models.Namespace,
            'provider_namespaces': models.ProviderNamespace,
            'repositories': models.Repository,
            'roles': models.Role,
        }
        session = self.get_session()
        for name, model in targets.items():
            json_objs = concat_json(self.json_dir / name)
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
                    depends = self.resolver.resolve(json_objs)
                    session.add_all(depends)
                session.commit()
            except Exception as e:
                logger.exception(str(e))
                session.rollback()
                logger.error("Rollback.")
                return False
        logger.info("Done")
        return True
