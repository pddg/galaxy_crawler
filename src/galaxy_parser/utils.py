from pathlib import Path
from urllib.parse import urlparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union


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
