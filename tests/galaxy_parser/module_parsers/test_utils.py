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
        actual = utils.get_base_name(command)
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
            utils.get_base_name(command)


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
        actual = utils.is_tmpl_var(sentence)
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
            utils.is_tmpl_var(sentence)


class TestParseCommands(object):

    @pytest.mark.parametrize(
        'script,expected', [
            ("echo Hello", [("echo", False)]),
            ("echo Hello | grep hello", [("echo", False), ("grep", False)]),
            ("echo $(dirname hoge)", [("echo", False), ("dirname", False)]),
            ("LC_ALL=C echo Hello", [("echo", False)]),
            ("echo Hello && echo World", [("echo", False), ("echo", False)]),
            ("echo Hello || echo World", [("echo", False), ("echo", False)]),
            ("echo Hello\necho World", [("echo", False), ("echo", False)]),
            ("if test -d /tmp; then echo Hello; else echo World; fi", [("test", False), ("echo", False), ("echo", False)]),
            ("ANSIBLE_VAR_UNDEF hoge fuga", [("ANSIBLE_VAR_UNDEF", True)]),
            ("echo Hello | ANSIBLE_VAR_UNDEF hello", [("echo", False), ("ANSIBLE_VAR_UNDEF", True)]),
        ]
    )
    def test_parse(self, script, expected):
        actual = utils.parse_commands('shell', script)
        assert actual == expected

    @pytest.mark.parametrize(
        "script,expected", [
            ("echo \nHello", [("echo", False)]),
            ("echo \nHello\n | \ngrep Hello", [("echo", False), ("grep", False)]),
            ("echo\n $(dirname\n hoge)", [("echo", False), ("dirname", False)]),
        ]
    )
    def test_parse_command_module(self, script, expected):
        actual = utils.parse_commands('command', script)
        assert actual == expected
