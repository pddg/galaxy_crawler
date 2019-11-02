import itertools

import pytest

from galaxy_crawler.models import v1 as models
from .base import ModelTestBase, create_provider, create_ns, create_session

ns_keys = ["email", "company", "location", "avatar_url", "html_url", "active", "namespace"]

namespaces = [
    {'id': 1, 'name': 'first'},
    {'id': 2, 'name': 'second'},
]

provider = {'id': 1, 'name': 'GitHub'}


def create_nsp_set():
    mail_set = ("example@example.com", None)
    company_set = ("hoge", None)
    location_set = ("fuga", None)
    avatar_set = ("https://avatars3.githubusercontent.com/u/hoge/fuga", None)
    html_url = ("https://example.com/", None)
    active_set = (True, False)
    ns_set = namespaces
    dataset = list(itertools.product(
        mail_set, company_set, location_set, avatar_set, html_url, active_set, ns_set))
    json_set = []
    id_count = 1
    for data in dataset:
        data_dict = dict(zip(ns_keys, data))
        ns = data_dict.pop("namespace")
        base = {
            "id": id_count,
            "name": "ns" + str(id_count),
            "display_name": "display_name" + str(id_count),
            "created": "2018-01-01T00:00:00.000000Z",
            "modified": "2018-01-01T01:00:00.000000Z",
            "summary_fields": {
                "namespace": ns,
                "provider": provider,
            },
            "followers": 0,
        }
        base.update(**data_dict)
        json_set.append(base)
        id_count += 1
    return json_set


class TestProviderNamespaceModel(ModelTestBase):

    def setup_method(self):
        super(TestProviderNamespaceModel, self).setup_method()
        s = create_session(self.engine)
        create_provider(s, **provider)
        for ns in namespaces:
            create_ns(s, **ns)
        s.commit()

    @pytest.mark.parametrize(
        "nsp_json", create_nsp_set()
    )
    def test_insert(self, nsp_json):
        sess = create_session(self.engine)
        nsp = models.ProviderNamespace.from_json(nsp_json, sess)
        sess.add(nsp)
        sess.commit()
        assert nsp.provider_namespace_id == nsp_json['id']
        for key in ns_keys + ["name"]:
            if key in ['namespace', 'provider']:
                actual = nsp_json['summary_fields'][key]
            else:
                actual = nsp_json[key]
            if key == 'active':
                expected = nsp.is_active
            elif key == 'followers':
                expected = nsp.followers_count
            elif key in ['namespace', 'provider']:
                related = getattr(nsp, key)
                expected = {
                    'id': getattr(related, key + '_id'),
                    'name': getattr(related, 'name'),
                }
            else:
                expected = getattr(nsp, key)
            assert expected == actual
        sess.close()
