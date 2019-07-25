import itertools

import pytest

from galaxy_crawler.models import v1 as model

from .base import ModelTestBase, create_session

ns_keys = ["email", "company", "location", "avatar_url", "html_url", "is_vendor"]


def create_ns_set():
    mail_set = ("example@example.com", None)
    company_set = ("hoge", None)
    location_set = ("fuga", None)
    avatar_set = ("https://avatars3.githubusercontent.com/u/hoge/fuga", None)
    html_url = ("https://example.com/", None)
    vendor_set = (True, False)
    dataset = list(itertools.product(
        mail_set, company_set, location_set, avatar_set, html_url, vendor_set))
    json_set = []
    id_count = 1
    for data in dataset:
        data_dict = dict(zip(ns_keys, data))
        base = {
            "id": id_count,
            "name": "ns" + str(id_count),
            "created": "2018-01-01T00:00:00.000000Z",
            "modified": "2018-01-01T01:00:00.000000Z",
        }
        base.update(**data_dict)
        json_set.append(base)
        id_count += 1
    return json_set


class TestNamespaceModel(ModelTestBase):

    @pytest.mark.parametrize(
        "ns_json", create_ns_set()
    )
    def test_insert(self, ns_json):
        sess = create_session(self.engine)
        ns = model.Namespace.from_json(ns_json, sess)
        sess.commit()
        assert ns.namespace_id == ns_json['id']
        for key in ns_keys + ["name"]:
            assert getattr(ns, key) == ns_json[key]
        sess.close()
