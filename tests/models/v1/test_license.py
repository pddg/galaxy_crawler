import pytest

from galaxy_crawler.models.base import LicenseType
from galaxy_crawler.models import v1 as model
from .base import ModelTestBase, create_session


class TestLicenseModel(ModelTestBase):

    @pytest.mark.parametrize(
        "license_str, expected", [
            ("MIT", [LicenseType.MIT]),
            ("GPLv3, Apache License", [LicenseType.GPLv3, LicenseType.APACHE]),
            ("other", ["other"])
        ]
    )
    def test_insert(self, license_str, expected):
        sess = create_session(self.engine)
        licenses = model.License.from_json({"license": license_str}, sess)
        sess.commit()
        assert len(licenses) == len(expected)
        actual_names = [l.name for l in licenses]
        actual_descs = [l.description for l in licenses]
        for e in expected:
            if isinstance(e, LicenseType):
                assert e.name in actual_names
                assert e.description in actual_descs
            else:
                assert e in actual_names
        sess.close()

    @pytest.mark.parametrize(
        "license_str, expected", [
            ("MIT", [LicenseType.MIT]),
            ("Apache 2.0 License, MIT", [LicenseType.MIT, LicenseType.APACHEv2]),
        ]
    )
    def test_get_exists(self, license_str, expected):
        sess = create_session(self.engine)
        licenses = []
        for e in expected:
            exists = sess.query(model.License).filter_by(name=e.name).one_or_none()
            if not exists:
                new_l = model.License(name=e.name, description=e.description)
                sess.add(new_l)
                licenses.append(new_l)
            else:
                licenses.append(exists)
        sess.commit()
        actual = model.License.from_json({"license": license_str}, sess)
        sess.commit()
        actual_ids = set([a.license_id for a in actual])
        expected_ids = set([l.license_id for l in licenses])
        assert actual_ids == expected_ids
