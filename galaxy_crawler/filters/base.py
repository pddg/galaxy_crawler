from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type


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

    def __init__(self, op: 'Type[Operand]', filter1: 'Type[Filter]', filter2: 'Type[Filter]'):
        self.op_class = op
        self.f1 = filter1()
        self.f2 = filter2()

    def __call__(self) -> 'Operand':
        return self.op_class(self.f1, self.f2)


class SingleOperandHolder(HolderMixin):

    def __init__(self, op: 'Type[SingleOperand]', filter1: 'Type[Filter]'):
        self.op_class = op
        self.f1 = filter1()

    def __call__(self) -> 'SingleOperand':
        return self.op_class(self.f1)


class BaseFilter(HolderMixin, type):
    pass


class Filter(metaclass=BaseFilter):
    """Filter base class"""

    @abstractmethod
    def passed(self, role: 'dict') -> bool:
        raise NotImplementedError


class DefaultFilter(Filter):

    def passed(self, role: 'dict') -> bool:
        return True
