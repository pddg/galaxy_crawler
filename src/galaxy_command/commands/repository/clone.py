import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import uroboros
from uroboros.constants import ExitStatus

from galaxy_command.commands.database.options import StorageOption
from galaxy_crawler.ghq import GHQ
from galaxy_crawler.models import helper

if TYPE_CHECKING:
    import argparse
    from typing import Union, List, Optional
    from galaxy_command.app.di import AppComponent

logger = logging.getLogger(__name__)

date_format = "%Y/%m/%d"


def _to_date(date_str: 'Optional[str]') -> 'Optional[datetime]':
    if date_str is not None:
        return datetime.strptime(date_str, date_format)
    return date_str


def _get_repository_urls(roles: 'pd.DataFrame') -> 'List[str]':
    return roles["repositories_clone_url"].values.tolist()


class CloneCommand(uroboros.Command):
    name = 'clone'
    short_description = 'Clone repositories'
    long_description = 'Clone repositories from GitHub based on given DB'
    options = [StorageOption()]

    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        errors = []
        p = args.percentile
        if not 0 < p < 1:
            errors.append(Exception(f"'percentile' must be grater than 0 and smaller than 1 ({p} is given)"))
        try:
            _to_date(args.date_from)
            _to_date(args.date_to)
        except Exception as e:
            errors.append(e)
        return errors

    def after_validate(self, safe_args: 'argparse.Namespace') -> 'argparse.Namespace':
        safe_args.date_from = _to_date(safe_args.date_from)
        safe_args.date_to = _to_date(safe_args.date_to)
        return safe_args

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument("output_dir",
                            type=Path,
                            help="Path to clone")
        parser.add_argument("--interval",
                            type=int,
                            default=5,
                            help="Clone interval")
        parser.add_argument("--percentile",
                            type=float,
                            default=0.9,
                            help="Threshold to clone")
        parser.add_argument("--n-jobs",
                            type=int,
                            default=6,
                            help="Number of parallel jobs")
        parser.add_argument("--date-from",
                            type=str,
                            help="Lower limit of modified date of role (YYYY/MM/DD)")
        parser.add_argument("--date-to",
                            type=str,
                            help="Upper limit of modified date of role (YYYY/MM/DD)")
        parser.add_argument("--dry-run",
                            action='store_true',
                            default=False,
                            help="Show the number of repository to clone (do not clone)")
        return parser

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        components = args.components  # type: AppComponent
        ghq_bin_path = Path('./bin/ghq').expanduser().resolve()
        ghq = GHQ(ghq_bin_path, args.output_dir)
        ghq.INTERVAL = args.interval
        ghq.N_JOBS = args.n_jobs
        try:
            engine = components.get_engine()

            # Get all roles as a pandas.DataFrame
            logger.info("Try to obtain roles from database")
            roles = helper.get_roles_df(engine, [3])
            logger.info(f"{len(roles)} roles were found")

            # Filtering by modified date
            from_date = args.date_from
            to_date = args.date_to
            if from_date is None:
                from_date = roles["modified"].min()
            if to_date is None:
                to_date = roles["modified"].max()
            logger.info(f"Filtering roles updated between {str(from_date)} and {str(to_date)}")
            roles = helper.filter_roles_df_by_modified_date(roles, from_date, to_date)
            logger.info(f"{len(roles)} roles were found")

            # Filtering by download count
            logger.info(f"Filtering roles by {args.percentile * 100} percentile")
            roles = helper.filter_roles_df_by_dl_percentile(roles, args.percentile)
            logger.info(f"{len(roles)} roles were found")

            repositories = _get_repository_urls(roles)
            if not args.dry_run:
                ghq.clone(repositories)
        except KeyboardInterrupt:
            return ExitStatus.FAILURE
        return ExitStatus.SUCCESS


command = CloneCommand()
