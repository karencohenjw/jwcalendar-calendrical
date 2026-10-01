"""Composable, inspectable date predicates."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from ..core.civil import CivilDate


class _HolidaySource(Protocol):
    def on(self, date: CivilDate) -> tuple[object, ...]: ...


class _BusinessSource(Protocol):
    def is_business_day(self, date: CivilDate) -> bool: ...


@dataclass(frozen=True, slots=True)
class Predicate:
    description: str
    test: Callable[[CivilDate], bool]

    def __call__(self, date: CivilDate) -> bool:
        return self.test(date)

    def __and__(self, other: Predicate) -> Predicate:
        return all_of(self, other)

    def __or__(self, other: Predicate) -> Predicate:
        return any_of(self, other)

    def __invert__(self) -> Predicate:
        return not_(self)


def all_of(*predicates: Predicate) -> Predicate:
    return Predicate("all_of", lambda d: all(p(d) for p in predicates))


def any_of(*predicates: Predicate) -> Predicate:
    return Predicate("any_of", lambda d: any(p(d) for p in predicates))


def not_(predicate: Predicate) -> Predicate:
    return Predicate(f"not({predicate.description})", lambda d: not predicate(d))


def weekday_is(weekday: int) -> Predicate:
    return Predicate(f"weekday_is({weekday})", lambda d: d.weekday() == weekday)


def month_is(month: int) -> Predicate:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1..12")
    return Predicate(f"month_is({month})", lambda d: d.month == month)


def day_of_month_is(day: int) -> Predicate:
    if not 1 <= day <= 31:
        raise ValueError("day must be 1..31")
    return Predicate(f"day_of_month_is({day})", lambda d: d.day == day)


def ordinal_between(first: int, last: int) -> Predicate:
    from ..systems.gregorian import day_of_year

    if not 1 <= first <= last <= 366:
        raise ValueError("ordinal range must be within 1..366")
    return Predicate(f"ordinal_between({first},{last})", lambda d: first <= day_of_year(d) <= last)


def iso_week_is(week: int) -> Predicate:
    from ..systems.iso_week import to_iso_week_date

    return Predicate(f"iso_week_is({week})", lambda d: to_iso_week_date(d)[1] == week)


def is_month_end() -> Predicate:
    from ..core.civil import days_in_month

    return Predicate("is_month_end", lambda d: d.day == days_in_month(d.year, d.month))


def is_year_boundary() -> Predicate:
    return Predicate("is_year_boundary", lambda d: (d.month, d.day) in {(1, 1), (12, 31)})


def holiday_is(calendar: _HolidaySource, holiday_id: str) -> Predicate:
    return Predicate(
        f"holiday_is({holiday_id})",
        lambda d: any(getattr(x, "id", None) == holiday_id for x in calendar.on(d)),
    )


def is_business_day(calendar: _BusinessSource) -> Predicate:
    return Predicate("is_business_day", lambda d: calendar.is_business_day(d))
