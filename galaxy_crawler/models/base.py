from enum import Enum
from abc import abstractmethod
from typing import TYPE_CHECKING

from galaxy_crawler.models import utils

if TYPE_CHECKING:
    from typing import List, Optional
    from sqlalchemy.orm.session import Session


class ModelInterfaceMixin(object):

    @classmethod
    @abstractmethod
    def from_json(cls, json_obj: 'dict', session: 'Session') -> 'ModelInterfaceMixin':
        raise NotImplementedError

    def exists(self, session: 'Session') -> 'bool':
        pk = getattr(self, self._pk, None)
        if pk is None:
            raise NotImplementedError('_pk is not imeplemented yet.')
        return session.query(self.__class__).get(pk)

    @classmethod
    def get_by_pk(cls, primary_key, session: 'Session') -> 'ModelInterfaceMixin':
        return session.query(cls).filter_by(**{cls._pk: primary_key}).one_or_none()

    def update_or_create(self, session: 'Session') -> 'ModelInterfaceMixin':
        if self.exists(session):
            pk = getattr(self, self._pk, None)
            if pk is None:
                raise NotImplementedError('_pk is not imeplemented yet.')
            exists_obj = self.get_by_pk(pk, session)
            return utils.update_params(exists_obj, self)
        return self


class RoleTypeEnum(Enum):
    ANS = "Ansible"
    CON = "Container Enabled"
    APP = "Container App"

    def description(self) -> str:
        return self.value


class LicenseType(Enum):
    MIT = 'MIT License'
    GPL = 'GNU General Public License'
    GPLv2 = 'GNU General Public License v2'
    GPLv3 = 'GNU General Public License v3'
    LGPL = 'GNU Lesser General Public License'
    LGPLv2 = 'GNU Lesser General Public License v2'
    LGPLv21 = 'GNU Lesser General Public License v2.1'
    LGPLv3 = 'GNU Lesser General Public License v3'
    AGPL = 'GNU Affero General Public License'
    AGPLv2 = 'GNU Affero General Public License v2'
    AGPLv3 = 'GNU Affero General Public License v3'
    APACHE = 'Apache License'
    APACHEv1 = 'Apache Software License 1.0'
    APACHEv11 = 'Apache Software License 1.1'
    APACHEv2 = 'Apache License 2.0'
    CC_BY = 'Creative Commons Attribution 4.0 license'
    CC_BY_SA = 'Creative Commons Attribution (Share Alike) 4.0 license'
    CC_BY_ND = 'Creative Commons Attribution (No Derivative Works) 4.0 license'
    CC_BY_NC = 'Creative Commons Attribution (Noncommercial) 4.0 license'
    CC_BY_NC_SA = 'Creative Commons Attribution (Noncommercial, Share Alike) 4.0 license'
    CC_BY_NC_ND = 'Creative Commons Attribution (Noncommercial, No Derivative Works) 4.0 license'
    CC0 = 'Creative Commons Zero'
    BSD = 'BSD License'
    BSD2 = 'BSD 2 Clause License'
    BSD3 = 'BSD 3 Clause License'
    APLv2 = 'Apple Public Source License v2'
    MPLv2 = 'Mozilla Public License v2'
    EPL = 'Eclipse Public License'
    CISCO = 'CISCO SAMPLE CODE LICENSE'

    @classmethod
    def normalize(cls, license_str: str) -> 'List[LicenseType]':
        splitted = license_str.split(',')
        licenses = []
        for string in splitted:
            licenses.append(parse_mit(string))
            licenses.append(parse_apache(string))
            licenses.append(parse_bsd(string))
            licenses.append(parse_cc(string))
            licenses.append(parse_gpl(string))
            licenses.append(parse_apl(string))
            licenses.append(parse_epl(string))
            licenses.append(parse_cisco(string))
        return list(set([l for l in licenses if l is not None]))

    @property
    def description(self) -> 'str':
        return self.value


def parse_mit(license_str: str) -> 'Optional[LicenseType]':
    if 'MIT' in license_str:
        return LicenseType.MIT
    return None


def parse_agpl(license_str: str) -> 'LicenseType':
    if '2' in license_str:
        return LicenseType.AGPLv2
    elif '3' in license_str:
        return LicenseType.AGPLv3
    else:
        return LicenseType.AGPL


def parse_lgpl(license_str: str) -> 'LicenseType':
    if '2.1' in license_str:
        return LicenseType.LGPLv21
    elif '2' in license_str:
        return LicenseType.LGPLv2
    elif '3' in license_str:
        return LicenseType.LGPLv3
    else:
        return LicenseType.LGPL


def parse_gpl(license_str: str) -> 'Optional[LicenseType]':
    license_type = None
    license_str = license_str.lower()
    if 'gnu' in license_str or 'gpl' in license_str:
        if 'agpl' in license_str or 'affelo' in license_str:
            license_type = parse_agpl(license_str)
        elif 'lgpl' in license_str or 'lesser' in license_str:
            license_type = parse_lgpl(license_str)
        elif '2' in license_str:
            license_type = LicenseType.GPLv2
        elif '3' in license_str:
            license_type = LicenseType.GPLv3
        else:
            license_type = LicenseType.GPL
    return license_type


def parse_cc(license_str: str) -> 'Optional[LicenseType]':
    license_type = None
    sa = False
    nc = False
    nd = False
    license_str = license_str.lower()
    if 'cc' in license_str or 'creative' in license_str:
        if 'sa' in license_str or 'share' in license_str:
            sa = True
        if 'nd' in license_str or 'derivative' in license_str:
            nd = True
        if 'nc' in license_str or 'commercial' in license_str:
            nc = True
        if nc:
            if sa:
                license_type = LicenseType.CC_BY_NC_SA
            elif nd:
                license_type = LicenseType.CC_BY_NC_ND
            else:
                license_type = LicenseType.CC_BY_NC
        elif sa:
            license_type = LicenseType.CC_BY_SA
        elif nd:
            license_type = LicenseType.CC_BY_ND
        elif 'zero' in license_str or '0' in license_str:
            license_type = LicenseType.CC0
        else:
            license_type = LicenseType.CC_BY
    return license_type


def parse_bsd(license_str: str) -> 'Optional[LicenseType]':
    license_type = None
    license_str = license_str.lower()
    if 'bsd' in license_str:
        if '2' in license_str:
            return LicenseType.BSD2
        elif '3' in license_str:
            return LicenseType.BSD3
        else:
            return LicenseType.BSD
    return license_type


def parse_apl(license_str: str) -> 'Optional[LicenseType]':
    if 'apple' in license_str.lower() or 'apl' in license_str.lower():
        return LicenseType.APLv2
    return None


def parse_apache(license_str: str) -> 'Optional[LicenseType]':
    if 'apache' in license_str.lower():
        if '2.0' in license_str or '2' in license_str:
            return LicenseType.APACHEv2
        elif '1.1' in license_str:
            return LicenseType.APACHEv11
        elif '1.0' in license_str or '1' in license_str:
            return LicenseType.APACHEv1
        else:
            return LicenseType.APACHE
    return None


def parse_cisco(license_str: str) -> 'Optional[LicenseType]':
    if 'cisco' in license_str.lower():
        return LicenseType.CISCO
    return None


def parse_epl(license_str: str) -> 'Optional[LicenseType]':
    license_str = license_str.lower()
    if 'epl' in license_str or 'eclipse' in license_str:
        return LicenseType.EPL
    return None
