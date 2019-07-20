import logging
from pathlib import Path
from typing import TYPE_CHECKING

import alembic
import alembic.config
import alembic.command
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import IntegrityError, NoForeignKeysError

from galaxy_crawler.repositories import RDBStorage
from galaxy_crawler.models import v1 as model
from galaxy_crawler.constants import Target

if TYPE_CHECKING:
    from typing import Any, List, Dict
    from alembic.config import Config as AlembicConfig
    from alembic.script import ScriptDirectory as AlembicScriptDir


logger = logging.getLogger(__name__)

model_target_pair = {
    Target.TAGS: model.Tag,
    Target.PROVIDERS: model.Provider,
    Target.PROVIDER_NAMESPACES: model.ProviderNamespace,
    Target.NAMESPACES: model.Namespace,
    Target.REPOSITORIES: model.Repository,
    Target.PLATFORMS: model.Platform,
    Target.ROLES: model.Role,
}


class RDBStore(RDBStorage):

    def __init__(self, engine):
        self.engine = engine
        self.session = scoped_session(sessionmaker(bind=engine))
        self.retry_queue = {}  # type: Dict[Target, List[dict]]
        model.BaseModel.metadata.create_all(self.engine)

    def _commit(self, target: 'Target', o: 'Any', session):
        try:
            session.commit()
        except (IntegrityError, NoForeignKeysError) as e:
            logger.error(e)
            session.rollback()
            if isinstance(e, NoForeignKeysError):
                if target not in self.retry_queue:
                    self.retry_queue[target] = []
                self.retry_queue[target].append(o)
            return False
        return True

    def save(self, target: 'Target', obj: 'Any') -> 'Any':
        session = self.session()
        model_class = model_target_pair.get(target)
        if model_class is None:
            raise ValueError(f'{target} is not supported.')
        if target in self.retry_queue:
            retry_objs = self.retry_queue.pop(target)
            obj = obj + retry_objs
        records = []
        for o in obj:
            record = model_class.from_json(o, session)
            session.flush()
            if self._commit(target, o, session):
                records.append(record)
        return records

    def is_migration_required(self) -> 'bool':
        script_dir = self._get_alembic_script_dir()
        head = script_dir.get_current_head()
        current = self._get_current_version()
        logger.debug(f"Schema version: Head-> {head} Current -> {current}")
        return head != current

    def migrate(self) -> 'None':
        conf = self._get_alembic_config()
        try:
            alembic.command.upgrade(conf, 'head')
        except Exception as e:
            logger.error(e)

    def _get_current_version(self) -> str:
        ctx = alembic.migration.MigrationContext.configure(self.engine.connect())
        rev = ctx.get_current_revision()
        return rev

    def _get_alembic_script_dir(self) -> 'AlembicScriptDir':
        conf = self._get_alembic_config()
        script = alembic.script.ScriptDirectory.from_config(conf)
        return script

    def _get_alembic_config(self) -> 'AlembicConfig':
        model_dir = Path(__file__).parent
        conf = alembic.config.Config(str(model_dir / 'alembic.ini'))

        conf.set_main_option('script_location', str(model_dir / 'alembic'))
        conf.set_main_option('sqlalchemy.url', str(self.engine.url))
        return conf

