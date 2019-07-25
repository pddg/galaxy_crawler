from sqlalchemy.orm.session import sessionmaker, Session

from galaxy_crawler.models import v1 as model
from galaxy_crawler.models import engine


def create_session(e) -> 'Session':
    return sessionmaker(bind=e)()


class ModelTestBase(object):

    def setup_method(self):
        self.engine = engine.get_in_memory_database()
        model.BaseModel.metadata.create_all(bind=self.engine)

    def teardown_method(self):
        model.BaseModel.metadata.drop_all(bind=self.engine)
