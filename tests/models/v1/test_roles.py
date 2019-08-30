import pytest
from sqlalchemy import or_

from galaxy_crawler.models import v1 as models

from .base import ModelTestBase, create_session, create_ns, \
    create_provider, create_provider_ns, create_platform, \
    create_tag, create_repository


class TestRoleModel(ModelTestBase):

    def setup_method(self):
        super(TestRoleModel, self).setup_method()
        sess = create_session(self.engine)
        create_provider(sess)
        ns = create_ns(sess)
        provider_ns = create_provider_ns(sess, namespace_id=ns.namespace_id)
        create_repository(sess, provider_ns_id=provider_ns.provider_namespace_id)
        create_platform(sess)
        for i, name in enumerate(["development", "system", "web"]):
            create_tag(sess, i, name)
        sess.commit()

    @pytest.mark.parametrize(
        "role_json", [
            {
                "id": 1,
                "summary_fields": {
                    "dependencies": [],
                    "namespace": {
                        "id": 1,
                        "name": "ns",
                        "avatar_url": "https://example.com/avatar",
                        "location": "Example Location",
                        "company": "Example Company",
                        "email": None,
                        "html_url": "https://example.com/test",
                        "is_vendor": False
                    },
                    "platforms": [
                        {
                            "name": "Ubuntu",
                            "release": "bionic"
                        }
                    ],
                    "provider_namespace": {
                        "id": 1,
                        "name": "test"
                    },
                    "repository": {
                        "id": 1,
                        "name": "test",
                        "original_name": "test",
                        "stargazers_count": 10,
                        "watchers_count": 10,
                        "forks_count": 10,
                        "open_issues_count": 10,
                        "travis_status_url": "https://travis-ci.org/example",
                        "travis_build_url": "https://travis-ci.org/example",
                        "format": "role",
                        "deprecated": False,
                        "community_score": 3.5,
                        "quality_score": 5.0,
                        "community_survey_count": 5
                    },
                    "tags": [
                        "development",
                        "system",
                        "web"
                    ],
                    "versions": [
                        {
                            "id": 1,
                            "name": "1.0.0",
                            "release_date": "2018-01-23T00:00:00Z"
                        },
                    ]
                },
                "created": "2014-01-23T00:00:00.000000Z",
                "modified": "2019-01-23T01:23:45.000000Z",
                "name": "test",
                "role_type": "ANS",
                "is_valid": True,
                "min_ansible_version": "2.4",
                "license": "license (BSD, MIT)",
                "company": "Example",
                "description": "Test",
                "travis_status_url": "https://travis-ci.org/example",
                "download_count": 100,
                "imported": "2019-01-23T00:00:00.000000-04:00",
                "active": True,
                "github_user": "test",
                "github_repo": "test-role",
                "github_branch": "master",
                "stargazers_count": 10,
                "forks_count": 0,
                "open_issues_count": 10,
                "commit": "b380413513177006b9641fd7ff960ea7d1051942",
                "commit_message": "Test",
                "commit_url": "https://example.com/commit",
                "issue_tracker_url": "https://example.com/issues"
            },
        ]
    )
    def test_insert(self, role_json):
        sess = create_session(self.engine)
        role = models.Role.from_json(role_json, sess)  # type: models.Role
        sess.commit()
        assert role.role_id == role_json.get("id")
        assert role.namespace.name == \
            role_json['summary_fields']['namespace']['name']
        assert role.repository.name == \
            role_json['summary_fields']['repository']['name']
        assert {l.name for l in role.licenses} == \
               {"BSD", "MIT"}
        assert {p.name for p in role.platforms} == \
               {"Ubuntu"}
        assert {v.name for v in role.versions} == \
               {"1.0.0"}
