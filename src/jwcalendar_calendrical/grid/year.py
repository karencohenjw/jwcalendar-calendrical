"""Structured twelve-month Gregorian year model."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.civil import CivilDate, is_leap_year
from ..systems.iso_week import weeks_in_iso_year
from .context import CalendarContext
from .month import MonthGrid, build_month


@dataclass(frozen=True, slots=True)
class CalendarYear:
    year: int
    leap: bool
    days: int
    iso_weeks: int
    months: tuple[MonthGrid, ...]
    month_start_weekdays: tuple[int, ...]
    holiday_index: tuple[tuple[str, tuple[CivilDate, ...]], ...]


def build_year(year: int, context: CalendarContext | None = None) -> CalendarYear:
    """Build all twelve month grids and useful year metadata."""
    if year < 1:
        raise ValueError("year must be >= 1")
    if context is None:
        context = CalendarContext()
    grids = tuple(
        build_month(
            year,
            month,
            week_model=context.week_model,
            weekend=context.weekend,
            holidays=context.holiday_calendar,
        )
        for month in range(1, 13)
    )
    occurrences = context.holiday_calendar.occurrences(year) if context.holiday_calendar else ()
    index = tuple((item.id, (item.legal_date, item.observed_date)) for item in occurrences)
    return CalendarYear(
        year,
        is_leap_year(year),
        366 if is_leap_year(year) else 365,
        weeks_in_iso_year(year),
        grids,
        tuple(CivilDate(year, month, 1).weekday() for month in range(1, 13)),
        index,
    )
