from galaxy_crawler.models import utils
from galaxy_crawler.models import v1 as model

from .base import ModelTestBase, create_session


class TestProviderModel(ModelTestBase):

    def test_insert(self):
        j = {
            "id": 1,
            "name": "GitHub",
            "description": "Public GitHub",
            "url": "/api/v1/providers/active/1/",
            "related": {},
            "summary_fields": {},
            "created": "2018-06-30T00:00:00Z",
            "modified": "2018-06-30T00:00:00Z",
            "active": True
        }
        sess = create_session(self.engine)
        provider = model.Provider.from_json(j, sess)
        sess.commit()
        assert provider.provider_id == j['id']
        assert provider.name == j['name']
        assert provider.description == j['description']
        assert utils.as_utc(provider.created) == utils.to_datetime(j['created'])
        assert utils.as_utc(provider.modified) == utils.to_datetime(j['modified'])
        assert provider.active == j['active']

        exists = model.Provider.from_json(j, sess)
        assert exists.provider_id == j['id']
