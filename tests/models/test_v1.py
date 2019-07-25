import pytest

from sqlalchemy.orm.session import sessionmaker, Session

from galaxy_crawler.models import v1 as model
from galaxy_crawler.models import engine
from galaxy_crawler.models import utils


def create_session(e) -> 'Session':
    return sessionmaker(bind=e)()


class ModelTestBase(object):

    def setup_method(self):
        self.engine = engine.get_in_memory_database()
        model.BaseModel.metadata.create_all(bind=self.engine)

    def teardown_method(self):
        model.BaseModel.metadata.drop_all(bind=self.engine)


class TestTags(ModelTestBase):

    @pytest.mark.parametrize(
        "tag", [
            {
              "id": 1,
              "url": "/api/v1/tags/1/",
              "related": {},
              "summary_fields": {},
              "created": "2018-01-23T10:00:00.000000Z",
              "modified": "2018-01-23T10:1:23.456789Z",
              "name": "test_tag",
              "active": True
            }, {
                "id": 2,
                "url": "/api/v1/tags/2/",
                "related": {},
                "summary_fields": {},
                "created": "2018-01-23T10:00:00.000000Z",
                "modified": "2018-01-23T10:1:23.456789Z",
                "name": "test_tag2",
                "active": False
            }
        ]
    )
    def test_insert(self, tag):
        sess = create_session(self.engine)
        inserted = model.Tag.from_json(tag, sess)
        sess.commit()
        assert inserted.tag_id == tag.get('id')
        assert inserted.name == tag.get('name')
        assert inserted.active == tag.get('active')
        assert utils.as_utc(inserted.created) == utils.to_datetime(tag.get('created'))
        assert utils.as_utc(inserted.modified) == utils.to_datetime(tag.get('modified'))
        sess.close()

    @pytest.mark.parametrize(
        "create, to_find, expected", [
            (['hoge'], 'hoge', 'hoge'),
            (['hoge', 'fuga'], 'hoge', 'hoge'),
            (['hoge', 'fuga'], ['hoge', 'fuga'], ['hoge', 'fuga']),
            (['hoge'], 'piyo', None),
            (['hoge'], ['hoge', 'piyo'], ['hoge'])
        ]
    )
    def test_find_by_name(self, create, to_find, expected):
        sess = create_session(self.engine)
        for i, name in enumerate(create):
            sess.add(model.Tag(tag_id=i+1, name=name))
        sess.commit()
        actual = model.Tag.find_by_name(to_find, sess)
        if not isinstance(actual, model.Tag) and actual is not None:
            assert len(actual) == len(expected)
            for act in actual:
                assert act.name in expected
        else:
            if expected:
                assert actual.name == expected
            else:
                # Expected is None
                assert actual == expected
        sess.close()
