import itertools
import pytest
from galaxy_crawler.filters import Filter, DefaultFilter


class DenyFilter(Filter):
    def passed(self, target, role: 'dict') -> bool:
        return False


test_cases = list(itertools.product([DefaultFilter(), DenyFilter()], repeat=2))


class TestFilter(object):

    @pytest.mark.parametrize(
        'expected,filters', [
            (f1.passed({}, {}) & f2.passed({}, {}), (f1, f2)) for f1, f2 in test_cases
        ]
    )
    def test_and(self, expected, filters):
        f1 = filters[0]
        f2 = filters[1]
        new_filter = (f1 & f2)()
        assert expected == new_filter.passed({}, {})

    @pytest.mark.parametrize(
        'expected,filters', [
            (f1.passed({}, {}) | f2.passed({}, {}), (f1, f2)) for f1, f2 in test_cases
        ]
    )
    def test_or(self, expected, filters):
        f1 = filters[0]
        f2 = filters[1]
        new_filter = (f1 | f2)()
        assert expected == new_filter.passed({}, {})

    @pytest.mark.parametrize(
        'expected,filter', [
            (f.passed({}, {}), f) for f in [DefaultFilter(), DenyFilter()]
        ]
    )
    def test_or(self, expected, filter):
        new_filter = not filter.passed({}, {})
        assert not expected == new_filter
