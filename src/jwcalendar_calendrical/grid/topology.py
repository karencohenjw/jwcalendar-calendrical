"""Formal structural descriptions of month and year grids."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.civil import CivilDate, days_in_month, is_leap_year
from ..week.calculations import weeks_in_year
from ..week.models import WeekModel
from .month import build_month


@dataclass(frozen=True, slots=True)
class MonthTopology:
    year: int
    month: int
    length: int
    starting_weekday: int
    row_count: int
    first_weekday: int
    minimal_days: int


@dataclass(frozen=True, slots=True)
class YearTopology:
    year: int
    leap: bool
    january_first_weekday: int
    month_sequence: tuple[tuple[int, int, int], ...]
    week_count: int
    first_weekday: int
    minimal_days: int


def month_topology(year: int, month: int, model: WeekModel) -> MonthTopology:
    return MonthTopology(
        year,
        month,
        days_in_month(year, month),
        CivilDate(year, month, 1).weekday(),
        build_month(year, month, week_model=model).row_count,
        model.first_weekday,
        model.minimal_days_in_first_week,
    )


def year_topology(year: int, model: WeekModel) -> YearTopology:
    return YearTopology(
        year,
        is_leap_year(year),
        CivilDate(year, 1, 1).weekday(),
        tuple((m, days_in_month(year, m), CivilDate(year, m, 1).weekday()) for m in range(1, 13)),
        weeks_in_year(year, model),
        model.first_weekday,
        model.minimal_days_in_first_week,
    )
