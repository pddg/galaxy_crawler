from typing import TYPE_CHECKING

import pandas as pd

from galaxy_crawler.models import utils
from galaxy_crawler.models import v1 as models

if TYPE_CHECKING:
    from datetime import datetime
    from typing import List, Optional
    from sqlalchemy.engine import Engine


def get_roles_df(engine: 'Engine', except_role_types: 'Optional[List[int]]' = None):
    """
    Obtain all roles with repository data as pandas.DataFrame
    :param engine: Database engine for connection
    :param except_role_types: Filtering role type based on given integers.
    :return: pandas.DataFrame
    """
    session = utils.get_scoped_session(engine)
    get_all_role_query = str(session.query(models.Role, models.Repository) \
                             .join(models.Repository, models.Role.repository_id == models.Repository.repository_id))
    role_df = pd.read_sql_query(get_all_role_query, engine, index_col=['roles_role_id'])
    # Remove column name prefix `roles_`
    role_df.rename(columns=lambda x: x[6:] if x.startswith("roles_") else x, inplace=True)
    if except_role_types is not None:
        # ~series.isin(some) indicate that `series not in some`
        role_df = role_df[~role_df["role_type_id"].isin(except_role_types)]
    return role_df


def filter_roles_df_by_modified_date(roles: 'pd.DataFrame',
                                     from_date: 'datetime',
                                     to_date: 'datetime') -> 'pd.DataFrame':
    """
    Filtering roles by the modified date.
    Returns only those with a value that was updated between `from_date` and `to_date`.
    :param roles: Roles DataFrame
    :param from_date: Lower threshold of modified datetime
    :param to_date: Upper threshold of modified datetime
    :return: pandas.DataFrame
    """
    if to_date <= from_date:
        to_date, from_date = from_date, to_date
    masks = (roles["modified"] <= to_date) & (roles["modified"] >= from_date)
    return roles.loc[masks]


def filter_roles_df_by_dl_percentile(roles: 'pd.DataFrame',
                                     percentile: 'float' = 0.9) -> 'pd.DataFrame':
    """
    Filtering roles by the number of downloads.
    Returns only those with a value greater than or equal to the specified percentile value.
    :param roles: Roles DataFrame
    :param percentile: 0 <= N <= 1
    :return: pandas.DataFrame
    """
    assert 0 <= percentile <= 1, "Percentile should be 0 <= N <= 1."
    threshold = roles['download_count'].quantile(percentile)
    masks = roles["download_count"] >= threshold
    return roles.loc[masks]
