"""ISO-8601 week dates (Monday-first, four-day minimum first week)."""

from __future__ import annotations

from ..core.civil import CivilDate
from ..core.errors import InvalidISOWeekDate
from .gregorian import fixed_to_gregorian, gregorian_to_fixed


def weeks_in_iso_year(year: int) -> int:
    """Return 52 or 53 ISO weeks in ``year``."""
    jan1_weekday = (gregorian_to_fixed(CivilDate(year, 1, 1)) - 1) % 7
    return (
        53
        if jan1_weekday == 3
        or (jan1_weekday == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)))
        else 52
    )


def to_iso_week_date(date: CivilDate) -> tuple[int, int, int]:
    """Return ``(ISO week-year, week number, ISO weekday 1..7)``."""
    weekday = date.weekday() + 1
    thursday = fixed_to_gregorian(gregorian_to_fixed(date) + 4 - weekday)
    jan4 = gregorian_to_fixed(CivilDate(thursday.year, 1, 4))
    week1_monday = jan4 - ((jan4 - 1) % 7)
    week = (gregorian_to_fixed(date) - week1_monday) // 7 + 1
    return thursday.year, week, weekday


def from_iso_week_date(year: int, week: int, weekday: int) -> CivilDate:
    """Construct a Gregorian date from a strict ISO week date."""
    if not 1 <= week <= weeks_in_iso_year(year) or not 1 <= weekday <= 7:
        raise InvalidISOWeekDate(f"invalid ISO week date: {year}-W{week:02d}-{weekday}")
    jan4 = gregorian_to_fixed(CivilDate(year, 1, 4))
    monday = jan4 - ((jan4 - 1) % 7)
    return fixed_to_gregorian(monday + 7 * (week - 1) + weekday - 1)


def iso_week_year(date: CivilDate) -> int:
    """Return the ISO week-year containing ``date``."""
    return to_iso_week_date(date)[0]
