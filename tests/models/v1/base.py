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


def create_provider(session: 'Session', id: int = 1, name: str = "GitHub") -> 'model.Provider':
    provider = model.Provider(provider_id=id, name=name, description="Test provider")
    session.add(provider)
    return provider


def create_ns(session: 'Session', id: int = 1, name: str = 'ns') -> 'model.Namespace':
    ns = model.Namespace(
        name=name, namespace_id=id
    )
    session.add(ns)
    return ns


def create_provider_ns(session: 'Session',
                       id: int = 1,
                       ns: str = "test",
                       provider_id: int = 1,
                       namespace_id: int = 1) -> 'model.ProviderNamespace':
    ns = model.ProviderNamespace(
        provider_namespace_id=id,
        name=ns,
        display_name=ns,
        provider_id=provider_id,
        namespace_id=namespace_id
    )
    session.add(ns)
    return ns


def create_platform(session: 'Session',
                    id: int = 1,
                    name: str = 'Ubuntu',
                    release: str = 'bionic'):
    platform = model.Platform(
        platform_id=id,
        name=name,
        release=release
    )
    session.add(platform)
    return platform


def create_tag(session: 'Session',
               id: int = 1,
               name: str = "system"):
    tag = model.Tag(
        tag_id=id,
        name=name
    )
    session.add(tag)
    return tag


def create_repository(session: 'Session',
                      id: int = 1,
                      name: str = 'test',
                      provider_ns_id: int = 1):
    repo = model.Repository(
        repository_id=id,
        name=name,
        provider_namespace_id=provider_ns_id
    )
    session.add(repo)
    return repo
