import pytest

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
