from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def to_absolute(path: 'Path'):
    if path is None:
        raise ValueError("Path must not be `None`")
    path = path.expanduser()
    if not path.is_absolute():
        path = path.absolute()
    return path


def mkdir(path: 'Path'):
    path = to_absolute(path)
    if not path.exists():
        path.mkdir(parents=True)
    else:
        if path.is_file():
            raise NotADirectoryError(f"'{path}' is not a directory.")
    return path
