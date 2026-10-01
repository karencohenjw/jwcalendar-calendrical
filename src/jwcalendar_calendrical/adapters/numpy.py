"""Optional NumPy helpers; importing this module requires the ``numpy`` extra."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from ..core.civil import CivilDate
from ..systems.gregorian import fixed_to_gregorian, gregorian_to_fixed


def gregorian_dates_to_fixed(dates: Iterable[CivilDate]) -> np.ndarray:
    """Convert an iterable of ``CivilDate`` values to an int64 array."""
    return np.asarray([gregorian_to_fixed(d) for d in dates], dtype=np.int64)


def fixed_days_to_gregorian(days: object) -> tuple[CivilDate, ...]:
    """Convert an array-like of fixed-day integers to immutable date values."""
    return tuple(fixed_to_gregorian(int(value)) for value in np.asarray(days).flat)
