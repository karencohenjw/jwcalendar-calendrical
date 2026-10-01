"""Julian civil-calendar arithmetic, explicitly separate from Julian Day Number."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.civil import CivilDate
from ..core.errors import InvalidCivilDate
from .gregorian import fixed_to_gregorian, gregorian_to_fixed


def julian_leap_year(year: int) -> bool:
    """Return whether a positive Julian calendar year is divisible by four."""
    if year < 1:
        raise ValueError("year must be >= 1; BCE years are unsupported")
    return year % 4 == 0


def julian_days_in_month(year: int, month: int) -> int:
    if year < 1 or not 1 <= month <= 12:
        raise ValueError("year must be >= 1 and month must be in 1..12")
    return (
        (29 if julian_leap_year(year) else 28)
        if month == 2
        else (31 if month in {1, 3, 5, 7, 8, 10, 12} else 30)
    )


@dataclass(frozen=True, slots=True, order=True)
class JulianDate:
    """A Julian civil-calendar date, with the Julian leap-year rule."""

    year: int
    month: int
    day: int

    def __post_init__(self) -> None:
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (self.year, self.month, self.day)
        ):
            raise InvalidCivilDate("Julian year, month, and day must be integers")
        if (
            self.year < 1
            or not 1 <= self.month <= 12
            or not 1 <= self.day <= julian_days_in_month(self.year, self.month)
        ):
            raise InvalidCivilDate(
                f"invalid Julian calendar date: {self.year}-{self.month}-{self.day}"
            )

    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d} (Julian)"


def julian_to_fixed(date: JulianDate) -> int:
    """Convert a Julian calendar date to a fixed day."""
    y, m, d = date.year, date.month, date.day
    prior = y - 1
    value = 365 * prior + prior // 4 + (367 * m - 362) // 12 + d - 2
    if m > 2:
        value -= 1 if julian_leap_year(y) else 2
    return value


def fixed_to_julian(fixed_day: int) -> JulianDate:
    """Convert a positive fixed day to a positive-year Julian calendar date."""
    if fixed_day < -1:
        raise ValueError("fixed day predates Julian year 1 in the supported year-numbering model")
    year = max(1, (fixed_day + 1) // 366)
    while julian_to_fixed(JulianDate(year + 1, 1, 1)) <= fixed_day:
        year += 1
    while julian_to_fixed(JulianDate(year, 1, 1)) > fixed_day:
        year -= 1
    ordinal = fixed_day - julian_to_fixed(JulianDate(year, 1, 1))
    month = 1
    while ordinal >= julian_days_in_month(year, month):
        ordinal -= julian_days_in_month(year, month)
        month += 1
    return JulianDate(year, month, ordinal + 1)


def gregorian_to_julian_calendar(date: CivilDate) -> JulianDate:
    """Return the Julian-calendar date on the same fixed day."""
    return fixed_to_julian(gregorian_to_fixed(date))


def julian_calendar_to_gregorian(date: JulianDate) -> CivilDate:
    """Interpret ``date`` in the Julian calendar and convert its day to Gregorian."""
    return fixed_to_gregorian(julian_to_fixed(date))


def to_julian_day_number(date: CivilDate, *, at_noon: bool = True) -> int | float:
    """Return astronomical Julian Date for Gregorian midnight/noon.

    Integer JDN labels the noon-to-noon Julian day. With ``at_noon=True`` this
    returns the integer JDN; at midnight it returns JDN minus 0.5.
    """
    jd_midnight = gregorian_to_fixed(date) + 1721424.5
    return int(jd_midnight + 0.5) if at_noon else jd_midnight


def from_julian_day_number(value: int | float) -> CivilDate:
    """Convert a Julian Date/JDN value to the Gregorian civil date containing it."""
    fixed = int(float(value) + 0.5) - 1721425
    return fixed_to_gregorian(fixed)
