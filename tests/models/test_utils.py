import copy
from datetime import datetime

import pytest
from pytz import timezone

from galaxy_crawler.models import utils


def role_stub(id_: int, name: str, depends: list) -> dict:
    namespace, role_name = name.split('.')
    return {
        'id': id_,
        'name': role_name,
        'summary_fields': {
            'namespace': {
                'name': namespace,
            },
            'dependencies': depends,
        }
    }


def create_depends(roles: list) -> 'list':
    return [role_stub(*r) for r in roles]


class TestResolveDependencies(object):

    @pytest.mark.parametrize(
        'roles,expected', [
            (
                    create_depends([
                        (0, 'a.role', ['b.role']),
                        (1, 'b.role', ['c.role']),
                        (2, 'c.role', ['a.role']),
                    ]),
                    [[1], [2], [0]]
            ), (
                    create_depends([
                        (0, 'a.role', ['a.role']),
                        (1, 'b.role', ['b.role']),
                        (2, 'c.role', ['c.role']),
                    ]),
                    [[0], [1], [2]]
            ), (
                    create_depends([
                        (0, 'a.role', ['a.role', 'b.role', 'c.role']),
                        (1, 'b.role', ['b.role', 'c.role']),
                        (2, 'c.role', ['c.role']),
                    ]),
                    [[0, 1, 2], [1, 2], [2]]
            ), (
                    create_depends([
                        (0, 'a.role', []),
                        (1, 'b.role', []),
                        (2, 'c.role', []),
                    ]),
                    [[], [], []]
            ), (
                    create_depends([
                        (0, 'a.role', ['d.role']),
                        (1, 'b.role', ['e.role']),
                        (2, 'c.role', ['f.role']),
                    ]),
                    [[], [], []]
            ), (
                    create_depends([
                        (0, 'a.role', ['a.no_role']),
                        (1, 'b.role', ['b.no_role']),
                        (2, 'c.role', ['c.no_role']),
                    ]),
                    [[], [], []]
            )
        ]
    )
    def test_resolve(self, roles, expected):
        resolved = utils.resolve_dependencies(roles)
        for res, e in zip(resolved, expected):
            actual = res['summary_fields']['dependencies']
            assert e == actual


class TestDatetimeRelated(object):

    DATE_FMT = "%Y-%m-%dT%H:%M:%S.%f%z"
    UTC = timezone("UTC")
    JST = timezone("Asia/Tokyo")

    @pytest.mark.parametrize(
        'dt, tz', [
            ("2018-01-23T12:34:56.789012Z", UTC),
            ("2018-01-23T12:34:56.789012+0900", JST),
        ]
    )
    def test_to_datetime(self, dt, tz):
        dt_obj = datetime.strptime(dt, self.DATE_FMT)
        dt_obj = dt_obj.astimezone(tz)
        actual = utils.to_datetime(dt_obj.strftime(self.DATE_FMT))
        assert actual == dt_obj
        assert actual.tzinfo == self.UTC

    @pytest.mark.parametrize(
        'dt', [
            datetime(2018, 1, 23, 12, 34, 56, 789012),
            datetime(2018, 1, 23, 12, 34, 56, 789012, tzinfo=JST),
        ]
    )
    def test_as_utc(self, dt):
        actual = utils.as_utc(dt)
        assert actual.tzinfo == self.UTC


class TestRoleName(object):

    ns = "namespace"
    role = "role"
    j = {
        "summary_fields": {
            "namespace": {
                "name": ns
            }
        },
        "name": role
    }

    def test_obtaining(self):
        expected = f"{self.ns}.{self.role}"
        assert utils.get_role_name_from_json(self.j) == expected

    @pytest.mark.parametrize(
        "pop_key", ["name", "summary_fields", ("name", "summary_fields")]
    )
    def test_obtaining_error(self, pop_key):
        j = copy.deepcopy(self.j)
        if isinstance(pop_key, str):
            j.pop(pop_key)
        else:
            for k in pop_key:
                j.pop(k)
        with pytest.raises(KeyError):
            utils.get_role_name_from_json(j)
