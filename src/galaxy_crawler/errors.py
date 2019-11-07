class NoSuchRecord(Exception):
    pass


class NoPrimaryKeyError(Exception):
    pass


class DateParseFailed(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class InvalidExpressionError(Exception):
    def __init__(self, expression: str):
        self.expr = expression

    def __str__(self):
        return f"Invalid Expression `{self.expr}`."


class NotSupportedFilterError(Exception):
    def __init__(self, filter_name: str):
        self.filter_name = filter_name

    def __str__(self):
        return f"Filter type '{self.filter_name}' is not supported."
