import pytest

from galaxy_crawler.models.base import LicenseType

test_cases = [
    ('MIT', [LicenseType.MIT]),
    ('GPL', [LicenseType.GPL]),
    ('GPLv2', [LicenseType.GPLv2]),
    ('GPLv3', [LicenseType.GPLv3]),
    ('GNU General Public License v3', [LicenseType.GPLv3]),
    ('LGPL', [LicenseType.LGPL]),
    ('LGPLv3', [LicenseType.LGPLv3]),
    ('LGPL-2.0', [LicenseType.LGPLv2]),
    ('GNU Lesser General Public License', [LicenseType.LGPL]),
    ('GNU Lesser General Public License v2.1', [LicenseType.LGPLv21]),
    ('Apache', [LicenseType.APACHE]),
    ('Apache Software License 1.0', [LicenseType.APACHEv1]),
    ('Apache Software License 1.1', [LicenseType.APACHEv11]),
    ('Apache License 2.0', [LicenseType.APACHEv2]),
    ('Apache-2.0', [LicenseType.APACHEv2]),
    ('CC-BY', [LicenseType.CC_BY]),
    ('CC-BY-SA', [LicenseType.CC_BY_SA]),
    ('CC-BY-NC', [LicenseType.CC_BY_NC]),
    ('CC-BY-NC-SA', [LicenseType.CC_BY_NC_SA]),
    ('CC-BY-NC-ND', [LicenseType.CC_BY_NC_ND]),
    ('CC-BY-ND', [LicenseType.CC_BY_ND]),
    ('CC0', [LicenseType.CC0]),
    ('CISCO SAMPLE CODE LICENSE', [LicenseType.CISCO]),
    ('EPL', [LicenseType.EPL]),
    ('license(BSD, GPLv2)', [LicenseType.BSD, LicenseType.GPLv2]),
    ('BSD-2-Clause', [LicenseType.BSD2]),
    ('BSD-3-Clause', [LicenseType.BSD3]),
    ('APLv2', [LicenseType.APLv2]),
    ('BSD MIT', [LicenseType.BSD, LicenseType.MIT]),
    ('other type', []),
]


class TestLicenseType(object):

    @pytest.mark.parametrize(
        'string,expected', test_cases
    )
    def test_normalize(self, string, expected):
        actual = LicenseType.normalize(string)
        assert len(expected) == len(actual)
        assert set(expected) == set(actual)

