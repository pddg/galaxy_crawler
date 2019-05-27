from threading import Thread
from queue import Queue
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List
    from galaxy_crawler.repositories import ResponseDataStore

logger = getLogger(__name__)


class ResponseParser(Thread):

    def __init__(self, url_queue: 'Queue', json_queue: 'Queue',
                 data_stores: 'List[ResponseDataStore]', query_builder):
        super(ResponseParser, self).__init__()
        self.url_q = url_queue
        self.json_q = json_queue
        self.data_stores = data_stores
        self.query_builder = query_builder
        self._stop_signal = False

    def run(self) -> None:
        while not self._stop_signal:
            json_obj = self.json_q.get()
            if json_obj is None:
                logger.info("Scraping finished")
                self.json_q.task_done()
                break
            if 'next_link' in json_obj:
                self.push_next_link(json_obj['next_link'])
            if 'results' not in json_obj:
                logger.critical("Failed to parse response. Returned json has no results.")
                break
            results = json_obj['results']
            logger.info(f"{len(results)} repositories were found.")
            for repository in results:
                # TODO: Support various thresholds
                if "download_count" in repository:
                    dl_count = repository["download_count"]
                    if dl_count < 500:
                        logger.info(f"Download count fell the below threshold ({dl_count})")
                        self.send_stop_signal()
                        break
                    try:
                        namespace = repository['summary_fields']['provider_namespace']['name']
                        logger.debug(f"{namespace}.{repository['name']}: {dl_count}")
                    except AttributeError:
                        logger.warning("This repository has no namespace")
                else:
                    logger.critical("Failed to parse response. Repository has no download count.")
                    self.send_stop_signal()
                    break
                for store in self.data_stores:
                    store.save(repository)
            self.json_q.task_done()
            if not self._stop_signal:
                logger.info("Wait for next response...")
        self.finish()

    def finish(self):
        logger.info("Saving obtained repositories information...")
        for store in self.data_stores:
            store.commit()
        logger.info("Parser finished")

    def send_stop_signal(self):
        self._stop_signal = True

    def push_next_link(self, link):
        next_link = self.query_builder.join(link)
        logger.info(f"Next link was found: {next_link}")
        self.url_q.put(next_link)

