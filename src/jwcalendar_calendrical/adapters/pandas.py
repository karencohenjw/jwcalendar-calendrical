"""Optional pandas helpers; importing this module requires the ``pandas`` extra."""

from __future__ import annotations

import pandas as pd

from ..systems.gregorian import gregorian_to_fixed


def dates_to_fixed(series: pd.Series) -> pd.Series:
    """Map a pandas Series of ``CivilDate`` objects to fixed-day integers."""
    return series.map(gregorian_to_fixed).astype("int64")


def fixed_to_dates(series: pd.Series) -> pd.Series:
    """Map a Series of fixed-day integers to ``CivilDate`` objects."""
    from ..systems.gregorian import fixed_to_gregorian

    return series.map(lambda value: fixed_to_gregorian(int(value)))
