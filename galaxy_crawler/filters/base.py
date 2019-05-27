from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING
from enum import Enum
from galaxy_crawler.errors import InvalidExpressionError

if TYPE_CHECKING:
    from typing import Type, Union, Tuple


class FilterEnum(Enum):

    @classmethod
    def choices(cls) -> 'Tuple[str]':
        choices = tuple(t.name.lower() for t in cls)  # type: Tuple[str]
        return choices

    @classmethod
    @abstractmethod
    def by_name(cls, name: str, gt: bool, threshold: 'Union[int, float]') -> 'Filter':
        """
        :param name: Name of the filter
        :param gt: Greater than
        :param threshold: Filter threshold
        :return:
        """
        raise NotImplementedError

    @classmethod
    def by_expr(cls, expr: str) -> 'Filter':
        operand = ">"
        if operand in expr:
            split_expr = [e.strip() for e in expr.split(operand)]
        elif "<" in expr:
            operand = "<"
            split_expr = [e.strip() for e in expr.split(operand)]
        else:
            split_expr = []
        if len(split_expr) != 2:
            raise InvalidExpressionError(expr)
        try:
            gt = operand == ">"
            threshold = float(split_expr[1])
        except ValueError:
            raise InvalidExpressionError(expr)
        return cls.by_name(split_expr[0], gt, threshold)


class HolderMixin:

    def __and__(self, other):
        return OperandHolder(AND, self, other)

    def __or__(self, other):
        return OperandHolder(OR, self, other)

    def __rand__(self, other):
        return OperandHolder(AND, other, self)

    def __ror__(self, other):
        return OperandHolder(OR, other, self)

    def __invert__(self):
        return SingleOperandHolder(NOT, self)


class SingleOperand(metaclass=ABCMeta):

    def __init__(self, filter1: 'Filter'):
        self.f = filter1

    @abstractmethod
    def passed(self, role: 'dict') -> bool:
        raise NotImplementedError


class NOT(SingleOperand):

    def passed(self, role: 'dict') -> bool:
        return not self.f.passed(role)


class Operand(metaclass=ABCMeta):

    def __init__(self, filter1: 'Filter', filter2: 'Filter'):
        self.f1 = filter1
        self.f2 = filter2

    @abstractmethod
    def passed(self, role: 'dict') -> bool:
        raise NotImplementedError


class AND(Operand):

    def passed(self, role: 'dict') -> bool:
        return self.f1.passed(role) and self.f2.passed(role)


class OR(Operand):

    def passed(self, role: 'dict') -> bool:
        return self.f1.passed(role) or self.f2.passed(role)


class OperandHolder(HolderMixin):

    def __init__(self, op: 'Type[Operand]', filter1: 'Filter', filter2: 'Filter'):
        self.op_class = op
        self.f1 = filter1
        self.f2 = filter2

    def __call__(self) -> 'Operand':
        return self.op_class(self.f1, self.f2)


class SingleOperandHolder(HolderMixin):

    def __init__(self, op: 'Type[SingleOperand]', filter1: 'Filter'):
        self.op_class = op
        self.f1 = filter1

    def __call__(self) -> 'SingleOperand':
        return self.op_class(self.f1)


class Filter(HolderMixin, metaclass=ABCMeta):
    """Filter base class"""

    @abstractmethod
    def passed(self, role: 'dict') -> bool:
        raise NotImplementedError


class DefaultFilter(Filter):

    def passed(self, role: 'dict') -> bool:
        return True
