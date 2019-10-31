import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import uroboros
from uroboros.constants import ExitStatus

from galaxy_crawler.ghq import GHQ
from galaxy_crawler.models import v1 as models
from galaxy_crawler.models.utils import get_scoped_session
from .database.options import StorageOption

if TYPE_CHECKING:
    import argparse
    from typing import Union
    from galaxy_crawler.app.di import AppComponent

logger = logging.getLogger(__name__)


def _get_roles_with_repos(engine) -> 'pd.DataFrame':
    session = get_scoped_session(engine)
    # Get all roles (except Container app) as pandas.DataFrame
    get_all_role_query = str(session.query(models.Role, models.Repository) \
                             .join(models.Repository, models.Role.repository_id == models.Repository.repository_id))
    logger.info("Try to obtain roles from database")
    role_df = pd.read_sql_query(get_all_role_query, engine, index_col=['roles_role_id'])
    # Remove column name prefix `roles_`
    role_df.rename(columns=lambda x: x[6:] if x.startswith("roles_") else x, inplace=True)
    # Filter to remove Container App
    role_df = role_df[role_df["role_type_id"] != 3]
    logger.info(f"{len(role_df)} roles were found")
    return role_df


def _get_roles_limited(roles: 'pd.DataFrame',
                       threshold: float,
                       last_updated_in: int = 365) -> 'pd.DataFrame':
    obtained_at = datetime(2019, 10, 22)
    year_ago = obtained_at - timedelta(days=last_updated_in)
    logger.info(f"Filtering roles updated between {str(obtained_at)} and {str(year_ago)}")
    recently_roles = roles.loc[obtained_at >= roles["modified"]]
    recently_roles = recently_roles.loc[roles["modified"] >= year_ago]
    logger.info(f"{len(recently_roles)} roles were found")
    logger.info(f"Filtering roles by {threshold * 100} percentile")
    threshold = _get_threshold(roles, threshold)
    popular_roles = recently_roles[recently_roles["download_count"] >= threshold]
    logger.info(f"{len(popular_roles)} roles were found")
    return popular_roles


def _get_threshold(roles: 'pd.DataFrame', percentile: float) -> 'pd.Series':
    """
    Obtain threshold by percentile
    """
    assert 0 <= percentile <= 1, "Percentile should be 0 <= N <= 1."
    # Updated recently
    return roles['download_count'].quantile(percentile)


def _get_repository_urls(roles: 'pd.DataFrame') -> 'List[str]':
    return roles["repositories_clone_url"].values.tolist()


class CloneCommand(uroboros.Command):
    name = 'clone'
    short_description = 'Clone repositories'
    long_description = 'Clone repositories from GitHub based on given DB'
    options = [StorageOption()]

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
        parser.add_argument("output_dir", type=Path, help="Path to clone")
        parser.add_argument("--interval", type=int, default=5, help="Clone interval")
        parser.add_argument("--percentile", type=float, default=0.9, help="Threshold to clone")
        parser.add_argument("--n-jobs", type=int, default=6, help="Number of parallel jobs")
        return parser

    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        components = args.components  # type: AppComponent
        ghq_bin_path = Path('./bin/ghq').expanduser().resolve()
        ghq = GHQ(ghq_bin_path, args.output_dir)
        ghq.INTERVAL = args.interval
        ghq.N_JOBS = args.n_jobs
        try:
            engine = components.get_engine()
            roles = _get_roles_with_repos(engine)
            roles = _get_roles_limited(roles, args.percentile)
            repositories = _get_repository_urls(roles)
            ghq.clone(repositories)
        except KeyboardInterrupt:
            return ExitStatus.FAILURE
        return ExitStatus.SUCCESS


command = CloneCommand()
