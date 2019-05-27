from unittest import TestCase
import itertools
from galaxy_crawler.filters import Filter, DefaultFilter


class DenyFilter(Filter):
    def passed(self, role: 'dict') -> bool:
        return False


class TestFilter(TestCase):

    def setUp(self) -> None:
        self.test_cases = list(itertools.product([DefaultFilter(), DenyFilter()], repeat=2))
        self.dummy_dict = dict()

    def test_and(self):
        ground_truth = [
            f1.passed(self.dummy_dict) & f2.passed(self.dummy_dict) for f1, f2 in self.test_cases
        ]
        for truth, filters in zip(ground_truth, self.test_cases):
            f1 = filters[0]
            f2 = filters[1]
            with self.subTest(f1=f1.__class__, f2=f2.__class__, truth=truth):
                new_filter = (f1 & f2)()
                self.assertEqual(truth, new_filter.passed(self.dummy_dict))

    def test_or(self):
        ground_truth = [
            f1.passed(self.dummy_dict) | f2.passed(self.dummy_dict) for f1, f2 in self.test_cases
        ]
        for truth, filters in zip(ground_truth, self.test_cases):
            f1 = filters[0]
            f2 = filters[1]
            with self.subTest(f1=f1.__class__, f2=f2.__class__, truth=truth):
                new_filter = (f1 | f2)()
                self.assertEqual(truth, new_filter.passed(self.dummy_dict))
