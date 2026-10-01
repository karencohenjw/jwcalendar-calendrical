"""Hypothesis strategies for downstream calendar tests (optional test extra)."""

from __future__ import annotations

from typing import Protocol

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

from ..core.civil import CivilDate, days_in_month


class _ReformSource(Protocol):
    def gap_dates(self) -> tuple[CivilDate, ...]: ...


def civil_dates(min_year: int = 1, max_year: int = 9999) -> SearchStrategy[CivilDate]:
    """Strategy generating valid dates in an explicit positive year range."""
    return st.integers(min_year, max_year).flatmap(
        lambda year: st.integers(1, 12).flatmap(
            lambda month: st.integers(1, days_in_month(year, month)).map(
                lambda day: CivilDate(year, month, day)
            )
        )
    )


def month_boundaries(min_year: int = 1, max_year: int = 9999) -> SearchStrategy[CivilDate]:
    return civil_dates(min_year, max_year).filter(
        lambda d: d.day == 1 or d.day == days_in_month(d.year, d.month)
    )


def iso_week_boundaries(min_year: int = 2, max_year: int = 9998) -> SearchStrategy[CivilDate]:
    from ..systems.iso_week import to_iso_week_date

    return civil_dates(min_year, max_year).filter(
        lambda d: (
            d.month in {1, 12} and (d.day <= 4 or d.day >= 28) and to_iso_week_date(d)[0] != d.year
        )
    )


def reform_boundaries(reform: _ReformSource) -> SearchStrategy[CivilDate]:
    return st.sampled_from([*reform.gap_dates()]) if reform.gap_dates() else st.nothing()


def valid_ordinal_dates(min_year: int = 1, max_year: int = 9999) -> SearchStrategy[CivilDate]:
    from ..core.civil import is_leap_year
    from ..systems.gregorian import from_ordinal_date

    return st.integers(min_year, max_year).flatmap(
        lambda year: st.integers(1, 366 if is_leap_year(year) else 365).map(
            lambda ordinal: from_ordinal_date(year, ordinal)
        )
    )
