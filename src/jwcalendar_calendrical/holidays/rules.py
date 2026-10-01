"""Inspectable, composable holiday-date rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..core.civil import CivilDate, days_in_month


class HolidayRule(Protocol):
    def dates(self, year: int) -> tuple[CivilDate, ...]: ...


@dataclass(frozen=True, slots=True)
class FixedDate:
    month: int
    day: int

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12 or not 1 <= self.day <= 31:
            raise ValueError("invalid fixed holiday")

    def dates(self, year: int) -> tuple[CivilDate, ...]:
        if self.day > days_in_month(year, self.month):
            return ()
        return (CivilDate(year, self.month, self.day),)


@dataclass(frozen=True, slots=True)
class NthWeekday:
    month: int
    weekday: int
    n: int

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12 or not 0 <= self.weekday <= 6 or not 1 <= self.n <= 5:
            raise ValueError("invalid NthWeekday")

    def dates(self, year: int) -> tuple[CivilDate, ...]:
        first = CivilDate(year, self.month, 1)
        day = 1 + (self.weekday - first.weekday()) % 7 + 7 * (self.n - 1)
        return (CivilDate(year, self.month, day),) if day <= days_in_month(year, self.month) else ()


@dataclass(frozen=True, slots=True)
class LastWeekday:
    month: int
    weekday: int

    def dates(self, year: int) -> tuple[CivilDate, ...]:
        last = CivilDate(year, self.month, days_in_month(year, self.month))
        return (last.add_days(-((last.weekday() - self.weekday) % 7)),)


@dataclass(frozen=True, slots=True)
class NearestWeekday:
    month: int
    day: int

    def dates(self, year: int) -> tuple[CivilDate, ...]:
        d = CivilDate(year, self.month, self.day)
        wd = d.weekday()
        return (d.add_days(-1 if wd == 5 else 1 if wd == 6 else 0),)


@dataclass(frozen=True, slots=True)
class RelativeToRule:
    base: HolidayRule
    offset_days: int

    def dates(self, year: int) -> tuple[CivilDate, ...]:
        return tuple(d.add_days(self.offset_days) for d in self.base.dates(year))


@dataclass(frozen=True, slots=True)
class ObservedRule:
    base: HolidayRule

    def dates(self, year: int) -> tuple[CivilDate, ...]:
        observed = []
        for d in self.base.dates(year):
            if d.weekday() == 5:
                observed.append(d.add_days(-1))
            elif d.weekday() == 6:
                observed.append(d.add_days(1))
            else:
                observed.append(d)
        return tuple(observed)


@dataclass(frozen=True, slots=True)
class UnionRule:
    rules: tuple[HolidayRule, ...]

    def dates(self, year: int) -> tuple[CivilDate, ...]:
        return tuple(sorted({d for rule in self.rules for d in rule.dates(year)}))
