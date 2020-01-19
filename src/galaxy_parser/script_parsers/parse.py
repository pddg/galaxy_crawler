from typing import TYPE_CHECKING

from bashlex import ast, parser

if TYPE_CHECKING:
    from typing import List


def as_ast(statement: str) -> 'List[ast.node]':
    """
    Parse given script and convert it to AST
    :param statement: Script statement to parse
    :return: AST of given statement
    """
    return parser.parse(statement)


class CommandParser(ast.nodevisitor):

    def __init__(self):
        self._commands = []

    def get_commands(self) -> 'List[str]':
        """
        Get all command word in the visited statement
        :return: List of command word
        """
        commands = []
        for c in self._commands:
            word = getattr(c, 'word', None)
            if word is None:
                continue
            commands.append(word)
        return commands

    def visitcommand(self, n, parts):
        try:
            i = 0
            length = len(parts)
            while True:
                if i >= length:
                    break
                command = parts[i]
                if command.kind != 'word':
                    i += 1
                else:
                    break
            if command.kind == 'word':
                self._commands.append(command)
        except IndexError:
            pass

