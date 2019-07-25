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


def create_provider(session: 'Session', id_: int = 1, name: str = "GitHub") -> 'model.Provider':
    provider = model.Provider(provider_id=id_, name=name, description="Test provider")
    session.add(provider)
    return provider


def create_provider_ns(session: 'Session', id_: int = 1, ns: str = "test", provider_id: int = 1):
    ns = model.ProviderNamespace(
        provider_namespace_id=id_,
        name=ns, display_name=ns, provider_id=provider_id
    )
    session.add(ns)
    return ns
