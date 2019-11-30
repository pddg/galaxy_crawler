import logging
import os
import time
import hashlib
from multiprocessing import Pool
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from tqdm import tqdm

if TYPE_CHECKING:
    from typing import Union, Callable, Any, List

logger = logging.getLogger(__name__)


def get_dump_name(role_name: str, version: str) -> 'str':
    m = hashlib.sha1()
    m.update(role_name.encode('utf-8'))
    m.update(version.encode('utf-8'))
    return m.hexdigest() + '.pickle'


def to_role_path(url: str) -> 'Path':
    """
    Convert GitHub url to local path
    eg. https://github.com/hoge/fuga.git -> Path('github.com/hoge/fuga')
    :param url: Url of repository
    :return:
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path
    if path.endswith('.git'):
        # Remove .git suffix
        path = path[:-4]
    # The `path` always starts with '/'
    return Path(domain) / path[1:]


def resolve(p: 'Path') -> 'Path':
    return p.expanduser().resolve()


def to_path(p: 'Union[str, Path]') -> 'Path':
    if isinstance(p, Path):
        return resolve(p)
    if isinstance(p, str):
        return resolve(Path(p))
    else:
        TypeError(f'str or Path is expected, got {p.__class__.__name__}')


def parallel(func: 'Callable[[Any], Any]', iterable: 'List[Any]', n_jobs: int = -1) -> 'List[Any]':
    if n_jobs < 0:
        n_jobs = os.cpu_count()
    if n_jobs > len(iterable):
        n_jobs = len(iterable)
    if n_jobs == 1:
        return [func(it) for it in iterable]
    with Pool(n_jobs) as pool:
        progress_bar = tqdm(total=len(iterable), leave=False)
        finished = 0
        results = [pool.apply_async(func, (it,)) for it in iterable]
        try:
            while True:
                time.sleep(0.5)
                statuses = [r.ready() for r in results]
                finished_now = statuses.count(True)
                progress_bar.update(finished_now - finished)
                finished = finished_now
                if all(statuses):
                    break
            results = [r.get(1) for r in results]
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            logger.error("SIGTERM Received. Shutdown workers.")
            pool.terminate()
            logger.error("Wait for shutting down...")
            pool.join()
        finally:
            progress_bar.close()
    return results
