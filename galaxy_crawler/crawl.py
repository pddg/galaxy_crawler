from logging import getLogger
from queue import Queue, Empty
from threading import Thread
from typing import TYPE_CHECKING
from time import sleep

import requests

if TYPE_CHECKING:
    from typing import Dict, Optional, Any

logger = getLogger(__name__)


class NoURLExists(Exception):
    pass


class RequestFailed(Exception):
    pass


class Crawler(Thread):
    """Obtaining json from API"""

    cache_key = 'crawler'
    base_headers = {"content-type": "application/json"}

    def __init__(self, url_queue: 'Queue', json_queue: 'Queue', wait_interval: int = 10, retry: int = 3,
                 continue_if_fail: bool = False):
        super(Crawler, self).__init__()
        self._url_queue = url_queue
        self._json_queue = json_queue
        self._stop_signal = False
        self._wait_interval = wait_interval
        self._retry = retry
        self._continue_if_fail = continue_if_fail
        self._custom_headers = dict()

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
            self._json_queue.put(data)
            self._url_queue.task_done()
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
                resp = requests.get(url, headers=self.get_headers())
                if resp.status_code != 200:
                    self.failed(f"{resp.status_code} '{url}' '{resp.json()}'")
                else:
                    logger.info(f"{resp.status_code}: {url}")
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

    def get_url(self) -> 'Optional[str]':
        retry_count = 0
        while True:
            try:
                url = self._url_queue.get(timeout=3)
                break
            except Empty:
                retry_count += 1
                if retry_count > self._retry:
                    url = None
                    break
                logger.info(f"No URL pushed to queue in 3 seconds. "
                            f"Retrying...{retry_count}/{self._retry}")
        if url is None:
            raise NoURLExists()
        return url

    def get_headers(self):
        return self.base_headers.update(self._custom_headers)

    def set_headers(self, header: 'Dict[str, str]'):
        self._custom_headers.update(header)

    def finish(self):
        logger.info("Crawler finished")

    def failed(self, msg: str):
        if not self._continue_if_fail:
            self.send_stop_signal()
        raise RequestFailed(msg)
