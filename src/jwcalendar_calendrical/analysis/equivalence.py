"""Search for years and months with equivalent structural layouts."""

from __future__ import annotations

from ..core.civil import CivilDate, days_in_month, is_leap_year
from ..grid.topology import year_topology
from ..week.models import WeekModel


def are_years_layout_equivalent(a: int, b: int, week_model: WeekModel) -> bool:
    """Compare month-grid shapes and week-model boundaries, ignoring holiday data."""
    return (
        year_topology(a, week_model).month_sequence == year_topology(b, week_model).month_sequence
        and year_topology(a, week_model).week_count == year_topology(b, week_model).week_count
        and is_leap_year(a) == is_leap_year(b)
    )


def find_equivalent_years(
    target_year: int, start: int, end: int, *, week_model: WeekModel
) -> tuple[int, ...]:
    """Return equivalent years in the inclusive interval, excluding the target."""
    target = year_topology(target_year, week_model)
    return tuple(
        y
        for y in range(start, end + 1)
        if y != target_year
        and year_topology(y, week_model).month_sequence == target.month_sequence
        and year_topology(y, week_model).week_count == target.week_count
        and is_leap_year(y) == target.leap
    )


def find_equivalent_months(
    year: int, month: int, start_year: int, end_year: int, *, week_model: WeekModel
) -> tuple[tuple[int, int], ...]:
    """Return (year, month) pairs whose month length and grid start match."""
    target = CivilDate(year, month, 1)
    sig = (days_in_month(year, month), target.weekday(), week_model.first_weekday)
    return tuple(
        (y, m)
        for y in range(start_year, end_year + 1)
        for m in range(1, 13)
        if (days_in_month(y, m), CivilDate(y, m, 1).weekday(), week_model.first_weekday) == sig
        and (y, m) != (year, month)
    )
