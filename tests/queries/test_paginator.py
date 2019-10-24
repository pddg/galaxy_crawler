import pytest

from galaxy_crawler.queries.v1 import Paginator


class TestPaginator(object):

    @pytest.mark.parametrize(
        "failed_at,expected", [
            ([], [(i+1, 100) for i in range(10)]),
            ([1], [(1, 100),
                   *[(i, 10) for i in range(1, 11)],
                   *[(i, 100) for i in range(2, 11)]]),
            ([2, 3], [(1, 100),
                      (2, 100),
                      (11, 10),
                      *[(i, 1) for i in range(101, 111)],
                      *[(i, 10) for i in range(12, 21)],
                      *[(i, 100) for i in range(3, 11)]]),
            ([2, 4], [(1, 100),
                      (2, 100),
                      (11, 10),
                      (12, 10),
                      *[(i, 1) for i in range(111, 121)],
                      *[(i, 10) for i in range(13, 21)],
                      *[(i, 100) for i in range(3, 11)]]),
        ],
    )
    def test_normal(self, failed_at, expected):
        results = []
        i = 0
        paginator = Paginator(100)
        while True:
            if i in failed_at:
                paginator.enter_failed_state()
            page = paginator.next_page()
            results.append(page)
            if page == (10, 100):
                break
            i += 1
        assert results == expected
