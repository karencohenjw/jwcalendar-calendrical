"""Structured date and year explanations composed from public primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..core.civil import CivilDate, days_in_month, is_leap_year
from ..grid.fingerprints import year_fingerprint
from ..holidays.calendar import HolidayCalendar
from ..systems.gregorian import gregorian_to_fixed, to_ordinal_date
from ..systems.iso_week import to_iso_week_date, weeks_in_iso_year
from ..systems.julian import gregorian_to_julian_calendar, to_julian_day_number
from ..week.calculations import week_of_year, week_year
from ..week.models import ISO, WeekModel
from .boundaries import analyze_date


class _BusinessCalendar(Protocol):
    def is_business_day(self, date: CivilDate) -> bool: ...


@dataclass(frozen=True, slots=True)
class DateExplanation:
    gregorian: str
    julian_calendar: str
    fixed_day: int
    julian_day_number: int | float
    ordinal_year: int
    ordinal_day: int
    weekday: int
    iso_week_year: int
    iso_week: int
    iso_weekday: int
    week_year: int
    week_number: int
    month_grid_row: int
    month_grid_column: int
    boundary_flags: tuple[str, ...]
    holiday_ids: tuple[str, ...]
    business_day: bool | None


def explain_date(
    date: CivilDate,
    *,
    holidays: HolidayCalendar | None = None,
    business_calendar: _BusinessCalendar | None = None,
    model: WeekModel = ISO,
) -> DateExplanation:
    iso_y, iso_w, iso_d = to_iso_week_date(date)
    analysis = analyze_date(date, holidays=holidays, model=model)
    leading = (CivilDate(date.year, date.month, 1).weekday() - model.first_weekday) % 7
    grid_row, grid_column = divmod(leading + date.day - 1, 7)
    return DateExplanation(
        str(date),
        str(gregorian_to_julian_calendar(date)),
        gregorian_to_fixed(date),
        to_julian_day_number(date),
        *to_ordinal_date(date),
        date.weekday(),
        iso_y,
        iso_w,
        iso_d,
        week_year(date, model),
        week_of_year(date, model),
        grid_row,
        grid_column,
        analysis.flags,
        analysis.holiday_ids,
        business_calendar.is_business_day(date) if business_calendar else None,
    )


@dataclass(frozen=True, slots=True)
class YearExplanation:
    year: int
    leap: bool
    days: int
    iso_weeks: int
    month_lengths: tuple[int, ...]
    month_start_weekdays: tuple[int, ...]
    fingerprint: dict[str, str]
    holidays: tuple[object, ...]


def explain_year(
    year: int, *, holidays: HolidayCalendar | None = None, model: WeekModel = ISO
) -> YearExplanation:
    occ = holidays.occurrences(year) if holidays else ()
    return YearExplanation(
        year,
        is_leap_year(year),
        366 if is_leap_year(year) else 365,
        weeks_in_iso_year(year),
        tuple(days_in_month(year, m) for m in range(1, 13)),
        tuple(CivilDate(year, m, 1).weekday() for m in range(1, 13)),
        year_fingerprint(year, model),
        occ,
    )
