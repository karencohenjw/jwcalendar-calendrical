"""Bounded iterator-based date search."""

from __future__ import annotations

from collections.abc import Iterator

from ..core.civil import CivilDate
from ..core.errors import SearchLimitExceeded
from .predicates import Predicate


def dates_between(
    start: CivilDate, end: CivilDate, where: Predicate, *, max_days: int = 3_660_000
) -> Iterator[CivilDate]:
    """Yield matching dates in the inclusive interval, in either direction."""
    step = 1 if end >= start else -1
    cur = start
    count = 0
    while cur <= end if step > 0 else cur >= end:
        if count >= max_days:
            raise SearchLimitExceeded(f"date scan exceeds max_days={max_days}")
        if where(cur):
            yield cur
        cur = cur.add_days(step)
        count += 1


def next_matching_date(
    start: CivilDate, where: Predicate, *, inclusive: bool = False, max_days: int = 3660
) -> CivilDate:
    cur = start if inclusive else start.add_days(1)
    for _ in range(max_days):
        if where(cur):
            return cur
        cur = cur.add_days(1)
    raise SearchLimitExceeded(f"no matching date found within {max_days} days")


def previous_matching_date(
    start: CivilDate, where: Predicate, *, inclusive: bool = False, max_days: int = 3660
) -> CivilDate:
    cur = start if inclusive else start.add_days(-1)
    for _ in range(max_days):
        if where(cur):
            return cur
        cur = cur.add_days(-1)
    raise SearchLimitExceeded(f"no matching date found within {max_days} days")
