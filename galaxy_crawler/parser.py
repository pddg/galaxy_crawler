from threading import Thread
from queue import Queue, Empty
from logging import getLogger
from typing import TYPE_CHECKING

from galaxy_crawler.crawl import Response, Request
from galaxy_crawler.constants import Target

if TYPE_CHECKING:
    from typing import List, Dict, Optional
    from galaxy_crawler.filters import Filter
    from galaxy_crawler.queries import QueryBuilder, QueryOrder
    from galaxy_crawler.repositories import ResponseDataStore

logger = getLogger(__name__)


class ResponseParser(Thread):

    def __init__(self, url_queue: 'Queue', json_queue: 'Queue', data_stores: 'List[ResponseDataStore]',
                 query_builder: 'QueryBuilder', order: 'QueryOrder', targets: 'List[Target]', filters: 'List[Filter]'):
        super(ResponseParser, self).__init__()
        self.url_q = url_queue
        self.json_q = json_queue
        self.data_stores = data_stores
        self.query_builder = query_builder
        self.filters = filters
        self.targets = targets
        self.order = order
        self._stop_signal = False
        self._save_trial = 0

    def run(self) -> None:
        try:
            for target in self.targets:
                if self._stop_signal:
                    break
                initial_url = self.get_url_from(target)
                self.push_next_link(target, initial_url)
                while not self._stop_signal:
                    try:
                        response = self.json_q.get(timeout=3)  # type: Optional[Response]
                    except Empty:
                        logger.debug("Wait for next response...")
                        continue
                    json_obj = response.response
                    if json_obj is None:
                        logger.info("Scraping finished")
                        self.json_q.task_done()
                        self.send_stop_signal()
                        break
                    results = json_obj.get('results')
                    if results is None:
                        logger.critical("Failed to parse response. Returned json has no results.")
                        self.send_stop_signal()
                        break
                    self.add_items(response.target, results)
                    self.save()
                    self.json_q.task_done()
                    next_link = json_obj.get('next_link')
                    if next_link is not None:
                        self.push_next_link(response.target, next_link)
                    else:
                        # Finish to obtain this kind of items
                        break
        finally:
            self.save()
            logger.info("Parser finished")
        return

    def make_request(self, target: 'Target', url: str) -> Request:
        return Request(target, url)

    def get_url_from(self, target: 'Target'):
        url = self.query_builder \
            .order_by(self.order) \
            .build(target)
        return url

    def add_items(self, target: 'Target', items: 'dict'):
        logger.info(f"{len(items)} items were found.")
        to_save = []
        for item in items:
            # Filtering objects
            if len(self.filters) > 0:
                if not all([f.passed(target, item) for f in self.filters]):
                    self.send_stop_signal()
                    break
            to_save.append(item)
        for store in self.data_stores:
            store.save(target, to_save)

    def save(self):
        self._save_trial += 1
        if self._save_trial % 5 == 0:
            logger.info("Saving obtained items information...")
            for store in self.data_stores:
                store.commit()

    def send_stop_signal(self):
        self._stop_signal = True

    def push_next_link(self, target: 'Target', link):
        next_link = self.query_builder.join(link)
        logger.info(f"Next link was found: {next_link}")
        self.url_q.put(self.make_request(target, next_link))

