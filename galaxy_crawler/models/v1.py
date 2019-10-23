from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from galaxy_crawler.models.base import LicenseType, ModelInterfaceMixin, RoleTypeEnum
from galaxy_crawler.models.errors import JSONParseFailed
from galaxy_crawler.utils import to_datetime

if TYPE_CHECKING:
    from typing import List, Dict, Any, Union
    from sqlalchemy.orm.session import Session

logger = getLogger(__name__)
BaseModel = declarative_base()

MAX_INDEXED_STR = 512


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
            parsed[parsed_key] = to_datetime(value)
        else:
            parsed[parsed_key] = value
    return parsed


class TagAssociation(BaseModel):
    __tablename__ = "tags_association"
    tag_id = Column(Integer,
                    ForeignKey('tags.tag_id'),
                    primary_key=True)
    role_id = Column(Integer,
                     ForeignKey('roles.role_id'),
                     primary_key=True)


class Tag(BaseModel, ModelInterfaceMixin):
    __tablename__ = "tags"
    tag_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(MAX_INDEXED_STR), unique=True)

    roles = relationship('Role',
                         uselist=True,
                         secondary=TagAssociation.__tablename__,
                         back_populates='tags',
                         cascade="all")
    active = Column(Boolean)
    created = Column(DateTime)  # type: datetime
    modified = Column(DateTime)  # type: datetime

    _pk = 'tag_id'

    @classmethod
    def from_json(cls, json_obj: 'Dict[Any, Any]', session: 'Session') -> 'Tag':
        parsed = parse_json(
            [
                {'key': cls._pk, 'target': 'id'},
                'name',
                'active',
                'created',
                'modified'
            ],
            json_obj, 'Tag')
        tag = Tag(**parsed)
        return tag

    @classmethod
    def find_by_name(cls, name: 'Union[str, List[str]]', session: 'Session'):
        if isinstance(name, list):
            results = session.query(cls) \
                .filter(cls.name.in_(name)).all()
        else:
            results = session.query(cls) \
                .filter(cls.name == name).one_or_none()
        return results

    def __str__(self):
        return f"Tag({self.tag_id}, '{self.name}')"


class LicenseStatus(BaseModel):
    __tablename__ = 'license_statuses'
    role_id = Column(Integer, ForeignKey('roles.role_id'), primary_key=True)
    license_id = Column(Integer, ForeignKey('licenses.license_id'), primary_key=True)


class License(BaseModel, ModelInterfaceMixin):
    __tablename__ = "licenses"
    license_id = Column(Integer, primary_key=True)
    name = Column(String(MAX_INDEXED_STR), unique=True)
    description = Column(String(MAX_INDEXED_STR))

    roles = relationship("Role",
                         uselist=True,
                         secondary=LicenseStatus.__tablename__,
                         back_populates='licenses')

    _pk = 'license_id'

    @classmethod
    def from_json(cls, json_obj: dict, session: 'Session') -> 'List[License]':
        license_str = json_obj['license']
        licenses = LicenseType.normalize(license_str)
        if len(licenses) == 0:
            exists = session.query(cls).filter_by(name=license_str).one_or_none()
            if exists is None:
                other_license = License(
                    name=license_str,
                    description='Other type license (could not categorize)'
                )
                records = [other_license]
            else:
                records = [exists]
        else:
            records = []
            for l in licenses:
                exists = session.query(cls).filter_by(name=l.name).one_or_none()
                if exists is None:
                    new_license = License(name=l.name, description=l.description)
                    records.append(new_license)
                else:
                    records.append(exists)
        return records


class PlatformStatus(BaseModel):
    __tablename__ = "platform_statuses"
    platform_id = Column(Integer, ForeignKey('platforms.platform_id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.role_id'), primary_key=True)


class Platform(BaseModel, ModelInterfaceMixin):
    __tablename__ = "platforms"
    # __table_args__ = (UniqueConstraint('name', 'release'),)
    platform_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(MAX_INDEXED_STR))
    release = Column(String(MAX_INDEXED_STR))
    active = Column(Boolean)
    created = Column(DateTime)  # type: datetime
    modified = Column(DateTime)  # type: datetime

    roles = relationship("Role",
                         secondary=PlatformStatus.__tablename__,
                         back_populates="platforms")

    _pk = 'platform_id'

    @classmethod
    def from_json(cls, json_obj: 'dict', session: 'Session') -> 'Platform':
        parsed = parse_json(
            [
                {'key': cls._pk, 'target': 'id'},
                'name',
                'release',
                'active',
                'created',
                'modified'
            ],
            json_obj, 'Platform'
        )
        platform = Platform(**parsed)
        return platform

    @classmethod
    def get_by_name(cls, name: str, release: str, session: 'Session') -> 'Platform':
        return session.query(cls) \
            .filter(cls.name == name) \
            .filter(cls.release == release) \
            .first()


class Provider(BaseModel, ModelInterfaceMixin):
    __tablename__ = "providers"
    provider_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(MAX_INDEXED_STR), unique=True)
    description = Column(String(MAX_INDEXED_STR))
    active = Column(Boolean)
    created = Column(DateTime)  # type: datetime
    modified = Column(DateTime)  # type: datetime

    provider_namespaces = relationship("ProviderNamespace",
                                       back_populates="provider",
                                       cascade="all, delete-orphan")

    _pk = 'provider_id'

    @classmethod
    def from_json(cls, json_obj: 'dict', session: 'Session') -> 'Provider':
        parsed = parse_json(
            [
                {'key': cls._pk, 'target': 'id'},
                'name',
                'description',
                'active',
                'created',
                'modified'
            ],
            json_obj, 'Provider'
        )
        provider = Provider(**parsed)
        return provider


class Namespace(BaseModel, ModelInterfaceMixin):
    """Namespace on Ansible Galaxy"""
    __tablename__ = "namespaces"
    namespace_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(MAX_INDEXED_STR), index=True, unique=True, nullable=False)
    company = Column(String(MAX_INDEXED_STR), nullable=True)
    email = Column(String(MAX_INDEXED_STR), nullable=True)
    location = Column(String(MAX_INDEXED_STR), nullable=True)
    avatar_url = Column(String(MAX_INDEXED_STR), nullable=True)
    html_url = Column(String(MAX_INDEXED_STR), nullable=True)
    is_vendor = Column(Boolean)
    created = Column(DateTime)
    modified = Column(DateTime)

    provider_namespace = relationship("ProviderNamespace",
                                      back_populates="namespace",
                                      single_parent=True,
                                      cascade="all, delete-orphan")
    roles = relationship("Role",
                         back_populates="namespace",
                         cascade="all, delete-orphan")

    _pk = 'namespace_id'

    @classmethod
    def from_json(cls, json_obj: 'dict', session: 'Session') -> 'Namespace':
        parsed = parse_json(
            [
                {'key': cls._pk, 'target': 'id'},
                'name',
                'company',
                'email',
                'location',
                'avatar_url',
                'html_url',
                'is_vendor',
                'created',
                'modified'
            ],
            json_obj, 'Namespace'
        )
        ns = Namespace(**parsed)
        return ns


class ProviderNamespace(BaseModel, ModelInterfaceMixin):
    """Namespace on remote git repository"""
    __tablename__ = "provider_namespaces"
    provider_namespace_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(MAX_INDEXED_STR), index=True, nullable=False)
    display_name = Column(String(MAX_INDEXED_STR))
    company = Column(String(MAX_INDEXED_STR), nullable=True)
    email = Column(String(MAX_INDEXED_STR), nullable=True)
    location = Column(String(MAX_INDEXED_STR), nullable=True)
    avatar_url = Column(String(MAX_INDEXED_STR), nullable=True)
    html_url = Column(String(MAX_INDEXED_STR), nullable=True)
    followers_count = Column(Integer)
    created = Column(DateTime)
    modified = Column(DateTime)

    provider_id = Column(Integer,
                         ForeignKey('providers.provider_id'), nullable=True)
    provider = relationship("Provider",
                            single_parent=True,
                            back_populates="provider_namespaces",
                            cascade="all, delete-orphan")  # type: Provider
    namespace_id = Column(Integer,
                          ForeignKey('namespaces.namespace_id'))
    namespace = relationship("Namespace",
                             single_parent=True,
                             back_populates="provider_namespace",
                             cascade="all, delete-orphan")  # type: Namespace
    repositories = relationship("Repository",
                                back_populates="provider_namespace",
                                cascade="all, delete-orphan")

    is_active = Column(Boolean, nullable=True)
    _pk = 'provider_namespace_id'

    @classmethod
    def from_json(cls, json_obj: 'dict', session: 'Session') -> 'ProviderNamespace':
        parsed = parse_json(
            [
                {'key': cls._pk, 'target': 'id'},
                'name',
                'email',
                'display_name',
                'company',
                'location',
                'avatar_url',
                'html_url',
                'created',
                {'key': 'followers_count', 'target': 'followers'},
                {'key': 'is_active', 'target': 'active'},
                'modified'
            ],
            json_obj, 'ProviderNamespace'
        )
        try:
            provider_id = json_obj['summary_fields']['provider']['id']
        except KeyError:
            provider_id = None
        try:
            namespace_id = json_obj['summary_fields']['namespace']['id']
        except KeyError:
            namespace_id = None
        provider_ns = ProviderNamespace(**parsed, provider_id=provider_id, namespace_id=namespace_id)
        return provider_ns


class Repository(BaseModel, ModelInterfaceMixin):
    """Git Repository"""
    __tablename__ = "repositories"
    __table_args__ = (UniqueConstraint('name', 'provider_namespace_id'),)

    repository_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(MAX_INDEXED_STR))
    readme = Column(Text, nullable=True)
    readme_html = Column(Text, nullable=True)

    # Related to git
    clone_url = Column(String(MAX_INDEXED_STR))
    issue_tracker_url = Column(String(MAX_INDEXED_STR))
    external_url = Column(String(MAX_INDEXED_STR))
    commit = Column(String(MAX_INDEXED_STR))
    commit_url = Column(String(MAX_INDEXED_STR))
    commit_message = Column(Text)
    commit_created = Column(DateTime)

    # Travis CI
    travis_build_url = Column(String(MAX_INDEXED_STR))
    travis_status_url = Column(String(MAX_INDEXED_STR))

    stargazers_count = Column(Integer)
    watchers_count = Column(Integer)
    forks_count = Column(Integer)
    open_issues_count = Column(Integer)
    community_score = Column(Integer, nullable=True)
    community_survey_count = Column(Integer, nullable=True)
    quality_score = Column(Integer, nullable=True)
    quality_score_date = Column(DateTime, nullable=True)

    deprecated = Column(Boolean)
    created = Column(DateTime)
    modified = Column(DateTime)

    provider_namespace_id = Column(Integer,
                                   ForeignKey('provider_namespaces.provider_namespace_id'))
    provider_namespace = relationship("ProviderNamespace",
                                      back_populates="repositories")  # type: ProviderNamespace
    roles = relationship("Role", back_populates="repository")
    versions = relationship("RepositoryVersion",
                            uselist=True,
                            back_populates="repository")  # type: RepositoryVersion

    _pk = 'repository_id'

    @classmethod
    def from_json(cls, json_obj: 'dict', session: 'Session') -> 'Repository':
        parsed = parse_json(
            [
                {'key': cls._pk, 'target': 'id'},
                'name',
                'readme',
                'readme_html',
                'clone_url',
                'issue_tracker_url',
                'external_url',
                'commit',
                'commit_url',
                'commit_message',
                'commit_created',
                'travis_build_url',
                'travis_status_url',
                'stargazers_count',
                'watchers_count',
                'forks_count',
                'open_issues_count',
                'community_score',
                'community_survey_count',
                'quality_score',
                'quality_score_date',
                'deprecated',
                'created',
                'modified'
            ],
            json_obj, 'Repository'
        )
        parsed['commit_created'] = to_datetime(parsed['commit_created'])
        parsed['quality_score_date'] = to_datetime(parsed['quality_score_date'])
        provider_namespace_id = json_obj['summary_fields']['provider_namespace']['id']
        pn = ProviderNamespace.get_by_pk(provider_namespace_id, session)
        repo = Repository(**parsed, provider_namespace=pn)
        return repo


class RoleType(BaseModel):
    __tablename__ = 'role_types'
    role_type_id = Column(Integer, primary_key=True)
    name = Column(String(8), unique=True)
    description = Column(String(MAX_INDEXED_STR))
    roles = relationship('Role', back_populates='role_type')

    @classmethod
    def get_by_name(cls, name: str, session: 'Session') -> 'RoleType':
        if name is None:
            role_type_enum = RoleTypeEnum.ANS
        else:
            role_type_enum = RoleTypeEnum[name.upper()]
        exists = session.query(cls) \
            .filter(cls.name == role_type_enum.name) \
            .one_or_none()
        if exists is None:
            role_type = RoleType(name=role_type_enum.name,
                                 description=role_type_enum.description())
            return role_type
        return exists


class RoleVersion(BaseModel):
    __tablename__ = "role_versions"
    role_id = Column(Integer, ForeignKey('roles.role_id'), primary_key=True)
    version_id = Column(Integer,
                        ForeignKey('repository_versions.version_id'),
                        primary_key=True)


class RepositoryVersion(BaseModel, ModelInterfaceMixin):
    __tablename__ = "repository_versions"
    version_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(MAX_INDEXED_STR))

    repository_id = Column(Integer, ForeignKey('repositories.repository_id'))
    repository = relationship("Repository", back_populates="versions")

    roles = relationship("Role",
                         secondary=RoleVersion.__tablename__,
                         uselist=True,
                         back_populates="versions")
    release_date = Column(DateTime)

    _pk = 'version_id'

    @classmethod
    def from_json(cls, json_obj: 'dict', session: 'Session') -> 'ModelInterfaceMixin':
        pass


class RoleDependency(BaseModel):
    __tablename__ = "role_dependencies"
    from_id = Column(Integer, ForeignKey('roles.role_id'), primary_key=True)
    to_id = Column(Integer, ForeignKey('roles.role_id'), primary_key=True)


class Role(BaseModel, ModelInterfaceMixin):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint('name', 'namespace_id', 'repository_id', 'role_type_id'),)
    role_id = Column(Integer, primary_key=True)
    name = Column(String(MAX_INDEXED_STR))
    description = Column(Text)

    role_type_id = Column(Integer, ForeignKey('role_types.role_type_id'))
    role_type = relationship("RoleType",
                             back_populates="roles")
    namespace_id = Column(Integer, ForeignKey('namespaces.namespace_id'))
    namespace = relationship("Namespace",
                             back_populates="roles")
    repository_id = Column(Integer, ForeignKey('repositories.repository_id'))
    repository = relationship("Repository",
                              back_populates="roles",
                              cascade='all')

    # Some metrics
    min_ansible_version = Column(String(10))
    download_count = Column(Integer)
    created = Column(DateTime)
    modified = Column(DateTime)

    deprecated = Column(Boolean)

    tags = relationship('Tag',
                        uselist=True,
                        secondary=TagAssociation.__tablename__,
                        back_populates='roles',
                        cascade='all')
    licenses = relationship('License',
                            uselist=True,
                            secondary=LicenseStatus.__tablename__,
                            back_populates='roles',
                            cascade='all')
    platforms = relationship('Platform',
                             uselist=True,
                             secondary=PlatformStatus.__tablename__,
                             back_populates='roles',
                             cascade='all')
    dependencies = relationship('Role',
                                uselist=True,
                                secondary=RoleDependency.__tablename__,
                                primaryjoin=(RoleDependency.from_id == role_id),
                                secondaryjoin=(RoleDependency.to_id == role_id),
                                back_populates='dependencies')
    versions = relationship('RepositoryVersion',
                            uselist=True,
                            secondary=RoleVersion.__tablename__,
                            back_populates='roles',
                            cascade='all')

    _pk = 'role_id'

    @classmethod
    def from_json(cls, json_obj: 'dict', session: 'Session') -> 'ModelInterfaceMixin':
        parsed = parse_json(
            [
                {'key': cls._pk, 'target': 'id'},
                'name',
                'description',
                'role_type',
                'min_ansible_version',
                'download_count',
                'created',
                'modified'
            ],
            json_obj, 'Role'
        )
        summary = json_obj['summary_fields']
        namespace_id = summary['namespace']['id']
        repository_id = summary['repository']['id']
        tags_str = summary['tags']
        versions_json = summary['versions']
        platforms_json = summary['platforms']
        licenses = License.from_json(json_obj, session)
        parsed['namespace_id'] = namespace_id
        parsed['repository_id'] = repository_id
        parsed['role_type'] = RoleType.get_by_name(parsed['role_type'], session)
        tags = Tag.find_by_name(tags_str, session)
        role = Role(**parsed)
        for t in tags:
            role.tags.append(t)
        for p in platforms_json:
            platform = Platform.get_by_name(p['name'], p['release'], session)
            role.platforms.append(platform)
        for l in licenses:
            role.licenses.append(l)
        for v in versions_json:
            version = RepositoryVersion(
                version_id=v['id'],
                name=v['name'],
                repository_id=repository_id,
                release_date=to_datetime(v['release_date']))
            role.versions.append(version)
        return role

    @classmethod
    def resolve_dependencies(cls, json_obj: 'dict', session: 'Session') -> 'bool':
        from_id = json_obj['id']
        depends = []
        for d in json_obj['summary_fields']['dependencies']:
            try:
                if session.query(RoleDependency).filter_by(from_id=from_id, to_id=d).one_or_none():
                    continue
                depends.append(RoleDependency(from_id=from_id, to_id=d))
            except Exception as e:
                logger.debug(e)

                logger.warning(f"Failed to resolve dependency from {from_id} to {d}")
                return False
        session.add_all(depends)
        return True
