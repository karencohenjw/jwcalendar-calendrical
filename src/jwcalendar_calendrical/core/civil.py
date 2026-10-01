"""Strict, timezone-free civil dates with astronomical year numbering omitted.

The supported year domain is the positive integers (1 AD and later). Gregorian
dates are proleptic: the Gregorian rules apply before their historical adoption.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import InvalidCivilDate

_MONTH_LENGTHS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def is_leap_year(year: int) -> bool:
    """Return whether a positive Gregorian year is a leap year."""
    if isinstance(year, bool) or not isinstance(year, int) or year < 1:
        raise ValueError("year must be >= 1; year zero and BCE dates are unsupported")
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    """Return a month's length, raising ``ValueError`` for invalid arguments."""
    if year < 1 or not 1 <= month <= 12:
        raise ValueError("year must be >= 1 and month must be in 1..12")
    return 29 if month == 2 and is_leap_year(year) else _MONTH_LENGTHS[month - 1]


def is_valid_date(year: int, month: int, day: int) -> bool:
    """Return whether the components form a valid proleptic Gregorian date."""
    if any(isinstance(value, bool) or not isinstance(value, int) for value in (year, month, day)):
        return False
    return year >= 1 and 1 <= month <= 12 and 1 <= day <= days_in_month(year, month)


@dataclass(frozen=True, slots=True, order=True)
class CivilDate:
    """An immutable Gregorian civil date, independent of time zones and clocks.

    Invalid component values are rejected rather than normalized. The supported
    year range starts at 1; astronomical year zero and BCE notation are omitted.
    """

    year: int
    month: int
    day: int

    def __post_init__(self) -> None:
        if not is_valid_date(self.year, self.month, self.day):
            raise InvalidCivilDate(
                f"invalid Gregorian civil date: {self.year}-{self.month}-{self.day}"
            )

    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def add_days(self, amount: int) -> CivilDate:
        """Return the date ``amount`` days away using exact integer arithmetic."""
        from ..systems.gregorian import fixed_to_gregorian, gregorian_to_fixed

        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("amount must be an integer number of days")
        return fixed_to_gregorian(gregorian_to_fixed(self) + amount)

    def add_months(self, amount: int, *, overflow: str = "clip") -> CivilDate:
        """Add calendar months; overflow is ``clip`` or ``raise``."""
        if overflow not in {"clip", "raise"}:
            raise ValueError("overflow must be 'clip' or 'raise'")
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("amount must be an integer number of months")
        index = self.year * 12 + self.month - 1 + amount
        year, month0 = divmod(index, 12)
        year += 0
        month = month0 + 1
        if year < 1:
            raise InvalidCivilDate("month arithmetic would leave the supported year domain")
        limit = days_in_month(year, month)
        if self.day > limit and overflow == "raise":
            raise InvalidCivilDate("target month does not contain the original day")
        return CivilDate(year, month, min(self.day, limit))

    def add_years(self, amount: int, *, overflow: str = "clip") -> CivilDate:
        """Add years; February 29 clips to February 28 unless ``overflow='raise'``."""
        return self.add_months(amount * 12, overflow=overflow)

    def weekday(self) -> int:
        """Return ISO weekday, Monday=0 through Sunday=6."""
        from ..systems.gregorian import gregorian_to_fixed

        return (gregorian_to_fixed(self) - 1) % 7


def add_days(date: CivilDate, amount: int) -> CivilDate:
    """Return ``date`` moved by an exact number of civil days."""
    return date.add_days(amount)


def add_months(date: CivilDate, amount: int, *, overflow: str = "clip") -> CivilDate:
    """Return ``date`` moved by calendar months under the selected overflow policy."""
    return date.add_months(amount, overflow=overflow)


def add_years(date: CivilDate, amount: int, *, overflow: str = "clip") -> CivilDate:
    """Return ``date`` moved by calendar years under the selected overflow policy."""
    return date.add_years(amount, overflow=overflow)


def days_between(start: CivilDate, end: CivilDate) -> int:
    """Return signed elapsed civil days from ``start`` to ``end``."""
    from ..systems.gregorian import gregorian_to_fixed

    return gregorian_to_fixed(end) - gregorian_to_fixed(start)


def weekday(date: CivilDate) -> int:
    """Return ISO weekday, Monday=0 through Sunday=6."""
    return date.weekday()
