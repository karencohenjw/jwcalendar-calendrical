"""Proleptic Gregorian arithmetic and ordinal date conversion."""

from __future__ import annotations

from ..core.civil import CivilDate, is_leap_year
from ..core.errors import InvalidOrdinalDate


def gregorian_to_fixed(date: CivilDate) -> int:
    """Convert a Gregorian date to fixed day (RD-style, 0001-01-01 is day 1)."""
    y, m, d = date.year, date.month, date.day
    prior = y - 1
    result = 365 * prior + prior // 4 - prior // 100 + prior // 400
    result += (367 * m - 362) // 12 + d
    if m > 2:
        result -= 1 if is_leap_year(y) else 2
    return result


def fixed_to_gregorian(fixed_day: int) -> CivilDate:
    """Convert a positive fixed day to its proleptic Gregorian date."""
    if isinstance(fixed_day, bool) or not isinstance(fixed_day, int):
        raise TypeError("fixed_day must be an integer")
    if fixed_day < 1:
        raise ValueError("fixed day must be >= 1 (the supported Gregorian domain)")
    n = fixed_day - 1
    n400, rem = divmod(n, 146097)
    year = n400 * 400 + 1
    # At most 400 small steps; avoids datetime limits and handles arbitrary years.
    year += rem // 365
    while True:
        start = 365 * (year - 1) + (year - 1) // 4 - (year - 1) // 100 + (year - 1) // 400
        if start < fixed_day:
            break
        year -= 1
    while True:
        start = 365 * year + year // 4 - year // 100 + year // 400
        if start >= fixed_day:
            break
        year += 1
    day_of_year = fixed_day - (
        365 * (year - 1) + (year - 1) // 4 - (year - 1) // 100 + (year - 1) // 400
    )
    month = 1
    while True:
        from ..core.civil import days_in_month

        length = days_in_month(year, month)
        if day_of_year <= length:
            return CivilDate(year, month, day_of_year)
        day_of_year -= length
        month += 1


def day_of_year(date: CivilDate) -> int:
    """Return the one-based ordinal day of the Gregorian year."""
    return gregorian_to_fixed(date) - gregorian_to_fixed(CivilDate(date.year, 1, 1)) + 1


def to_ordinal_date(date: CivilDate) -> tuple[int, int]:
    """Return ``(year, one_based_day_of_year)``."""
    return date.year, day_of_year(date)


def from_ordinal_date(year: int, ordinal: int) -> CivilDate:
    """Construct a Gregorian date from a strict one-based ordinal."""
    maximum = 366 if is_leap_year(year) else 365
    if ordinal < 1 or ordinal > maximum:
        raise InvalidOrdinalDate(f"ordinal {ordinal} is outside 1..{maximum} for {year}")
    return fixed_to_gregorian(gregorian_to_fixed(CivilDate(year, 1, 1)) + ordinal - 1)


def days_remaining_in_year(date: CivilDate) -> int:
    """Return the number of days after ``date`` through December 31."""
    return (366 if is_leap_year(date.year) else 365) - day_of_year(date)
