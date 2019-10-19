import logging
from typing import TYPE_CHECKING
from threading import Lock
from datetime import datetime
import colorlog

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional

_lock = Lock()

_cli_log_handler = None  # type: Optional[logging.Handler]
_file_log_handler = None  # type: Optional[logging.Handler]

_log_format = "%(log_color)s[%(asctime)s %(levelname)s]%(reset)s (%(name)s) %(message)s"
_file_log_format = "[%(asctime)s %(levelname)s] (%(name)s) %(message)s"
_log_file_name = "%Y-%m-%d_%H-%M-%S.log"


def _create_file_log_formatter():
    return logging.Formatter(_file_log_format)


def _create_default_formatter():
    return colorlog.ColoredFormatter(_log_format)


def _get_cli_handler(formatter: 'logging.Formatter'):
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    return handler


def _get_file_handler(formatter: 'logging.Formatter', logging_path: 'Path'):
    now = datetime.now()
    log_file = logging_path / now.strftime(_log_file_name)
    handler = logging.FileHandler(str(log_file))
    handler.setFormatter(formatter)
    return handler


def _get_lib_logger():
    return logging.getLogger(__name__.split(".")[0])


def _is_configured(handler: 'logging.Handler'):
    root_logger = logging.getLogger()
    if handler in root_logger.handlers:
        return True
    lib_logger = _get_lib_logger()
    if handler in lib_logger.handlers:
        return True
    return False


def _configure_root(log_level: int):
    root_logger = logging.getLogger()
    if root_logger.level != log_level:
        root_logger.setLevel(log_level)


def enable_stream_handler(log_level: int = logging.INFO):
    global _cli_log_handler
    with _lock:
        if _cli_log_handler is None:
            default_formatter = _create_default_formatter()
            _cli_log_handler = _get_cli_handler(default_formatter)
        if _is_configured(_cli_log_handler):
            return
        _configure_root(log_level)
        lib_logger = _get_lib_logger()
        lib_logger.addHandler(_cli_log_handler)
        lib_logger.setLevel(log_level)
        alembic_logger = logging.getLogger('alembic')
        alembic_logger.addHandler(_cli_log_handler)
        alembic_logger.setLevel(log_level)


def enable_file_logger(logging_path: 'Path', log_level: int = logging.INFO):
    global _file_log_handler
    with _lock:
        if _file_log_handler is None:
            default_formatter = _create_file_log_formatter()
            _file_log_handler = _get_file_handler(default_formatter, logging_path)
        if _is_configured(_file_log_handler):
            return
        lib_logger = _get_lib_logger()
        lib_logger.addHandler(_file_log_handler)
        lib_logger.setLevel(log_level)
        alembic_logger = logging.getLogger('alembic')
        alembic_logger.addHandler(_file_log_handler)
        alembic_logger.setLevel(log_level)
