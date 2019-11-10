import pytest

from pathlib import Path

from galaxy_parser import utils


class TestToRolePath(object):

    @pytest.mark.parametrize(
        "url,expected", [
            ('https://github.com/hoge/fuga', Path('github.com/hoge/fuga')),
            ('https://github.com/hoge/fuga.git', Path('github.com/hoge/fuga'))
        ]
    )
    def test_normal(self, url, expected):
        actual = utils.to_role_path(url)
        assert actual == expected
