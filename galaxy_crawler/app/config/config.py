import distutils
import argparse
import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from galaxy_crawler.queries.v1 import V1QueryOrder
from galaxy_crawler.filters.v1 import V1FilterEnum
from galaxy_crawler.constants import Target

if TYPE_CHECKING:
    from typing import Union, List, Optional
    from argparse import Namespace


def _output_warn(config_name: 'Optional[str]') -> None:
    if config_name:
        warnings.warn(f"Cannot parse {config_name}. Use default value instead.")


def strtobool(value: str, config_name: str = None) -> 'Optional[bool]':
    try:
        value = bool(distutils.utils.strtobool(value))
    except ValueError:
        _output_warn(config_name)
        value = None
    return value


def strtoint(value: str, config_name: str = None) -> 'Optional[int]':
    try:
        value = int(value)
    except ValueError:
        _output_warn(config_name)
        value = None
    return value


def reject_none(dict_obj: 'dict') -> 'dict':
    """Remove the item whose value is `None`"""
    return {k: v for k, v in dict_obj.items() if v is not None}


class Config(object):
    ENV_VARS_PREFIX = "GALAXY_CRAWLER_"

    # Default values
    DEFAULT_VERSION = 'v1'
    DEFAULT_INTERVAL = 10
    DEFAULT_RETRY = 3
    DEFAULT_DEBUG = False
    DEFAULT_OUTPUT_FORMAT = ['json']
    DEFAULT_ORDER_BY = "download"
    DEFAULT_FILTERS = []

    def __init__(self, output_dir: 'Path', version: str, interval: int, retry: int, output_format: 'List[str]',
                 debug: 'bool', order_by: str, inverse: bool, filters: 'List[str]', log_dir: 'Path' = None, **kwargs):
        assert interval >= 0, "Interval must be a positive value."
        assert retry >= 0, "Retry must be a positive value."
        self.output_dir = output_dir
        self.version = version
        self.interval = interval
        self.output_format = output_format
        self.retry = retry
        self.debug = debug
        self.log_dir = log_dir
        self.order_by = order_by
        self.inverse = inverse
        self.filters = filters
        # TODO: To support to select targets by option
        self.targets = [
            Target.TAGS,
            Target.PLATFORMS,
            Target.PROVIDERS,
            Target.NAMESPACES,
            Target.PROVIDER_NAMESPACES,
            Target.ROLES
        ]

    @classmethod
    def load(cls, args: 'Union[Namespace, dict]') -> 'Config':
        args_keys, args_config = cls._load_args_values(args)
        default_config = cls._load_default_values(args_keys)
        env_config = cls._load_env_vars(args_keys)

        # Configuration priority: Command line arg > Environment var > Default var
        final_config = default_config
        final_config.update(env_config)
        final_config.update(args_config)

        return cls(**final_config)

    @classmethod
    def _load_args_values(cls, args: 'Union[Namespace, dict]') -> 'List[str], dict':
        # Convert Namespace object to dictionary
        if type(args) != dict:
            args_dict = vars(args)
        else:
            args_dict = args
        # Obtain keys from argument parsers
        args_keys = [k for k, _ in args_dict.items()]
        # Remove `None` values
        args_config = reject_none(args_dict)
        return args_keys, args_config

    @classmethod
    def _load_env_vars(cls, keys: 'List[str]') -> 'dict':
        """Load configurations from environment variables"""
        config_dict = dict()
        env_vars = os.environ
        for key in keys:
            env_key = cls.ENV_VARS_PREFIX + key.upper()
            if key not in env_vars:
                continue
            value = os.getenv(env_key)
            if key.lower() in ["debug", "inverse"]:
                value = strtobool(value, env_key)
            elif key.lower() in ["interval", "retry"]:
                value = strtoint(value, env_key)
            elif key.lower() in ["output_format", "filters"]:
                value = [v.strip().lower() for v in value.split(",")]
            config_dict[key] = value
        return reject_none(config_dict)

    @classmethod
    def _load_default_values(cls, keys: 'List[str]') -> 'dict':
        """Load default values"""
        config_dict = dict()
        for key in keys:
            config_key = "DEFAULT_" + key.upper()
            config_dict[key] = getattr(cls, config_key, None)
        return config_dict

    @classmethod
    def get_parser(cls) -> 'argparse.ArgumentParser':
        parser = argparse.ArgumentParser(description="Ansible Galaxy crawler")

        log_parser = argparse.ArgumentParser(add_help=False)
        log_group = log_parser.add_argument_group("LOGGING")
        log_group.add_argument("--debug", action="store_true", default=False, help="Enable debug logging")
        log_group.add_argument("--log-dir", type=Path, help="Log output directory")

        cmd_parser = parser.add_subparsers(dest="func")
        start_cmd = cmd_parser.add_parser("start", help="Start crawling", parents=[log_parser])
        start_cmd.add_argument("output_dir", type=Path, help="Path to output")
        start_cmd.add_argument("--version", choices=["v1"], help="The API version of galaxy.ansible.com")
        start_cmd.add_argument("--interval", type=int,
                               help=f"Fetch interval (default={cls.DEFAULT_INTERVAL})")
        start_cmd.add_argument("--retry", type=int,
                               help=f"Number of retrying (default={cls.DEFAULT_RETRY})")
        start_cmd.add_argument("--format", choices=["json"], nargs="+", dest='output_format',
                               help=f"Output format (default={cls.DEFAULT_OUTPUT_FORMAT})")
        start_cmd.add_argument("--order-by", choices=V1QueryOrder.choices(),
                               help=f"Query order (default={cls.DEFAULT_ORDER_BY}). It is a descending order by default.")
        start_cmd.add_argument("--inverse", action="store_true",
                               help="If this specified, make the order of query inverse")
        start_cmd.add_argument("--filters", type=str, nargs='*',
                               help=f"Filter expression (e.g. download>500). "
                               f"Available filter types are {V1FilterEnum.choices()}")
        return parser
