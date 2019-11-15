import pytest

from galaxy_parser.module_parsers import utils


class TestSplitCommand(object):

    @pytest.mark.parametrize(
        'command,expected', [
            ('echo hello', ['echo', 'hello']),
            ('echo "Hello world"', ['echo', 'Hello world']),
            ('echo "Hello world" > /tmp/hello', ['echo', 'Hello world', '>', '/tmp/hello']),
            ('cat hello.txt | tr -s "\n" > hello.txt', ['cat', 'hello.txt', '|', 'tr', '-s', '\n', '>', 'hello.txt']),
        ]
    )
    def test_normal(self, command, expected):
        actual = utils.split_command(command)
        assert actual == expected

    @pytest.mark.parametrize(
        'command,err', [
            (1, TypeError),
            (0.5, TypeError),
            ([], TypeError),
            ({}, TypeError),
            (True, TypeError),
        ]
    )
    def test_error(self, command, err):
        with pytest.raises(err):
            utils.split_command(command)


class TestGetBaseName(object):

    @pytest.mark.parametrize(
        "command,expected", [
            ('echo', 'echo'),
            ('/bin/echo', 'echo'),
            ('./bin/echo', 'echo'),
            ('/bin/hoge command.exe', 'hoge command.exe'),
            ('{{ hoge }}', '{{ hoge }}'),
            ('/bin/{{ hoge }}', '{{ hoge }}')
        ]
    )
    def test_normal(self, command, expected):
        actual = utils.get_base_name(command)
        assert actual == expected

    @pytest.mark.parametrize(
        'command,err', [
            (1, TypeError),
            (0.5, TypeError),
            ([], TypeError),
            ({}, TypeError),
            (True, TypeError),
        ]
    )
    def test_error(self, command, err):
        with pytest.raises(err):
            utils.get_base_name(command)


class TestFindCommand(object):
    @pytest.mark.parametrize(
        "command,expected", [
            (['echo'], 'echo'),
            (['/bin/echo', 'fuga'], 'echo'),
            (['./bin/echo', 'piyo'], 'echo'),
            (['{{hoge}}', 'fuga'], '{{hoge}}'),
            (['{{', 'hoge}}', 'fuga'], '{{ hoge}}'),
            (['{{hoge', '}}', 'fuga'], '{{hoge }}'),
            (['{{', 'hoge', '}}', 'fuga'], '{{ hoge }}'),
            (['/bin/{{hoge}}', 'fuga'], '{{hoge}}'),
            (['/bin/{{', 'hoge}}', 'fuga'], '{{ hoge}}'),
            (['/bin/{{hoge', '}}', 'fuga'], '{{hoge }}'),
            (['/bin/{{', 'hoge', '}}', 'fuga'], '{{ hoge }}'),
            (['{{hoge}}/echo', 'fuga'], 'echo'),
            (['{{', 'hoge}}/echo', 'fuga'], 'echo'),
            (['{{hoge', '}}/echo', 'fuga'], 'echo'),
            (['{{ hoge }}/echo', 'fuga'], 'echo'),
            (['{{', 'hoge', '}}/{{', 'fuga', '}}', 'fuga'], '{{ fuga }}'),
            (['{{', 'hoge', '}}/{{fuga', '}}', 'fuga'], '{{fuga }}'),
            (['{{', 'hoge', '}}/{{', 'fuga}}', 'fuga'], '{{ fuga}}'),
            (['{{', 'hoge', '}}/{{', 'fuga', '}}', 'fuga'], '{{ fuga }}'),
        ]
    )
    def test_normal(self, command, expected):
        actual = utils.find_command(command)
        assert actual == expected

    @pytest.mark.parametrize(
        "command,expected", [
            ([], AssertionError),
            (1, TypeError),
            (0.5, TypeError),
            ([], AssertionError),
            ({}, AssertionError),
            (True, TypeError),
        ]
    )
    def test_error(self, command, expected):
        with pytest.raises(expected):
            utils.find_command(command)


class TestIsTmplVariable(object):

    @pytest.mark.parametrize(
        'sentence,expected', [
            ('{{ hoge }}', True),
            ('{{hoge}}', True),
            ('{{ hoge}}', True),
            ('{{hoge }}', True),
            ('{ hoge }', False),
            ('{{ hoge', False),
            ('hoge }}', False)
        ]
    )
    def test_normal(self, sentence, expected):
        actual = utils.is_tmpl_variable(sentence)
        assert actual is expected

    @pytest.mark.parametrize(
        'sentence,err', [
            (1, TypeError),
            (0.5, TypeError),
            ([], TypeError),
            ({}, TypeError),
            (True, TypeError),
        ]
    )
    def test_error(self, sentence, err):
        with pytest.raises(err):
            utils.is_tmpl_variable(sentence)
