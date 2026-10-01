"""Boundary risk analysis for calendar software."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.civil import CivilDate, days_in_month, is_leap_year
from ..holidays.calendar import HolidayCalendar
from ..systems.iso_week import to_iso_week_date
from ..systems.reform import ReformCalendar
from ..week.models import ISO, WeekModel


@dataclass(frozen=True, slots=True)
class BoundaryAnalysis:
    date: CivilDate
    flags: tuple[str, ...]
    holiday_ids: tuple[str, ...] = ()


def analyze_date(
    date: CivilDate,
    *,
    holidays: HolidayCalendar | None = None,
    model: WeekModel = ISO,
    reform: ReformCalendar | None = None,
) -> BoundaryAnalysis:
    flags = []
    if date.day == 1:
        flags.append("month_start")
    if date.day == days_in_month(date.year, date.month):
        flags.append("month_end")
    if (date.month, date.day) == (1, 1):
        flags.append("year_start")
    if (date.month, date.day) == (12, 31):
        flags.append("year_end")
    if (date.month, date.day) == (2, 29):
        flags.append("leap_day")
    if (date.month, date.day) in {(2, 28), (3, 1)} and is_leap_year(date.year):
        flags.append("adjacent_to_leap_day")
    iso_year, iso_week, _ = to_iso_week_date(date)
    if iso_year != date.year:
        flags.append("iso_week_year_mismatch")
    if iso_week == 53:
        flags.append("week_53")
    if reform:
        old_edge = CivilDate(
            reform.last_old_style_date.year,
            reform.last_old_style_date.month,
            reform.last_old_style_date.day,
        )
        if date in {old_edge, reform.first_new_style_date}:
            flags.append("calendar_reform_boundary")
    occ = holidays.on(date) if holidays else ()
    if occ:
        flags.append("holiday")
    if any(x.observed_date == date and x.legal_date != date for x in occ):
        flags.append("observed_holiday")
    return BoundaryAnalysis(date, tuple(flags), tuple(x.id for x in occ))


def scan_boundaries(
    year: int,
    *,
    holidays: HolidayCalendar | None = None,
    model: WeekModel = ISO,
    reform: ReformCalendar | None = None,
) -> tuple[BoundaryAnalysis, ...]:
    """Return dates with at least one high-risk boundary or holiday flag."""
    out = []
    for month in range(1, 13):
        candidates = {1, days_in_month(year, month)}
        if month == 2:
            candidates.update({28, 29})
        for day in candidates:
            try:
                d = CivilDate(year, month, day)
            except ValueError:
                continue
            item = analyze_date(d, holidays=holidays, model=model, reform=reform)
            if item.flags:
                out.append(item)
    return tuple(sorted(out, key=lambda x: x.date))
