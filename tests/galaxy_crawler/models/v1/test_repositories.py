import pytest

from galaxy_crawler.models import v1 as models
from .base import ModelTestBase, create_session, create_provider, create_ns, create_provider_ns


class TestRepositoryModel(ModelTestBase):

    def setup_method(self):
        super(TestRepositoryModel, self).setup_method()
        sess = create_session(self.engine)
        create_provider(sess)
        create_ns(sess)
        create_provider_ns(sess)
        sess.commit()

    @pytest.mark.parametrize(
        "repo_json", [
            {
                "id": 25194,
                "url": "/api/v1/repositories/25194/",
                "summary_fields": {
                    "provider_namespace": {
                        "name": "test",
                        "id": 1
                    },
                    "provider": {
                        "name": "GitHub",
                        "id": 1
                    },
                    "namespace": {
                        "id": 1,
                        "name": "test",
                        "description": "description",
                        "is_vendor": False
                    },
                },
                "created": "2016-02-29T20:29:58.006066Z",
                "modified": "2019-06-19T05:54:28.931393Z",
                "name": "test",
                "original_name": "ansible-role-test",
                "description": "Test role",
                "format": "role",
                "import_branch": "master",
                "is_enabled": True,
                "commit": "b380413513177006b9641fd7ff960ea7d1051942",
                "commit_message": "test",
                "commit_url": "https://example.com/commit_url",
                "commit_created": "2019-05-16T23:15:02-04:00",
                "stargazers_count": 10,
                "watchers_count": 0,
                "forks_count": 1,
                "open_issues_count": 14,
                "download_count": 1,
                "travis_build_url": "https://travis-ci.org/build_url",
                "travis_status_url": "https://travis-ci.org/status_url",
                "clone_url": "https://github.com/ns1/test",
                "external_url": "https://github.com/ns1/test",
                "issue_tracker_url": "https://github.com/ns1/test/issues",
                "readme": None,
                "readme_html": None,
                "download_url": "https://github.com/ns1/test/archive/1.0.0.tar.gz",
                "deprecated": False,
                "community_score": 3.69565217391304,
                "quality_score": 5.0,
                "quality_score_date": "2019-06-13T19:29:09.123917-04:00",
                "community_survey_count": 6,
                "active": None
            }
        ]
    )
    def test_insert(self, repo_json):
        sess = create_session(self.engine)
        repo = models.Repository.from_json(repo_json, sess)
        sess.add(repo)
        sess.commit()
        assert repo.repository_id == repo_json['id']
        assert repo.provider_namespace.provider_namespace_id == \
            repo_json['summary_fields']['provider_namespace']['id']
