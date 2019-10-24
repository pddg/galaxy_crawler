from logging import getLogger
from queue import Queue
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING

import requests

from galaxy_crawler.queries import QueryOrder, QueryBuilder
from galaxy_crawler.queries.v1 import Paginator

if TYPE_CHECKING:
    from galaxy_crawler.constants import Target
    from typing import Dict, Any, List

logger = getLogger(__name__)


class NoURLExists(Exception):
    pass


class RequestFailed(Exception):
    pass


class Response(object):

    def __init__(self, target: 'Target', response: dict):
        self.target = target
        self.response = response


class Crawler(Thread):
    """Obtaining json from API"""

    cache_key = 'crawler'
    base_headers = {"content-type": "application/json"}

    def __init__(self,
                 targets: 'List[Target]',
                 query_builder: 'QueryBuilder',
                 order: 'QueryOrder',
                 json_queue: 'Queue',
                 wait_interval: int = 10,
                 retry: int = 3):
        super(Crawler, self).__init__()
        self.targets = targets
        self.current_target = targets[0]
        self.query_builder = query_builder
        self.order = order
        self._json_queue = json_queue
        self._stop_signal = False
        self._wait_interval = wait_interval
        self._retry = retry
        self._custom_headers = dict()
        self._paginator = Paginator(100)

    def send_stop_signal(self):
        self._stop_signal = True

    def run(self) -> None:
        """Access to the API at regular interval"""
        while True:
            if self._stop_signal:
                break
            try:
                url = self.get_url()
            except NoURLExists:
                break
            try:
                data = self.get_json(url)
            except RequestFailed as e:
                logger.error(e.args)
                continue
            if data is None:
                continue
            res = Response(self.current_target, data)
            self._json_queue.put(res)
            self.sleep()
        self.finish()

    def sleep(self):
        logger.info(f"Wait for {self._wait_interval} sec")
        sleep(self._wait_interval)

    def get_json(self, url) -> 'Dict[str, Any]':
        done = False
        data = None
        failed_count = 0
        while failed_count < self._retry and not done:
            try:
                resp = requests.get(url, headers=self.get_headers(), timeout=(30, 60))
                if resp.status_code != 200:
                    logger.warning(f"{resp.status_code}: '{url}'")
                    if resp.status_code == 404:
                        logger.info(f"Done: {self.current_target.name}")
                        self.next_target()
                        return data
                    elif resp.status_code == 500:
                        page_size = self._paginator.extract_page_size(url)
                        if page_size == 1:
                            logger.warning(f"Skip due to 500: {url}")
                            return data
                        else:
                            self._paginator.enter_failed_state()
                            return data
                    else:
                        resp.raise_for_status()
                else:
                    logger.info(f"{resp.status_code}: '{url}'")
                done = True
            except Exception as e:
                failed_count += 1
                if failed_count > self._retry:
                    self.failed(f"Retry count over the threshold.")
                    done = True
                else:
                    logger.error(f"Request to '{url}' was failed with {e}. "
                                 f"Retrying...{failed_count}/{self._retry}")
                continue
            data = resp.json()
        return data

    def get_url(self) -> 'str':
        if self.current_target is None:
            raise NoURLExists()
        url = self.query_builder \
            .order_by(self.order) \
            .set_page(self._paginator.next_page()) \
            .build(self.current_target)
        return url

    def get_headers(self):
        return self.base_headers.update(self._custom_headers)

    def set_headers(self, header: 'Dict[str, str]'):
        self._custom_headers.update(header)

    def finish(self):
        logger.info("Crawler finished")

    def failed(self, msg: str):
        self.send_stop_signal()
        raise RequestFailed(msg)

    def next_target(self):
        idx = self.targets.index(self.current_target)
        try:
            self.current_target = self.targets[idx + 1]
        except IndexError:
            self.current_target = None
        self._paginator = Paginator(100)
