"""Immutable composition of calendar, week, holiday, and weekend semantics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..core.civil import CivilDate
from ..week.models import ISO, WeekModel


class HolidaySource(Protocol):
    def on(self, date: CivilDate) -> tuple[HolidayInfo, ...]: ...

    def occurrences(self, year: int) -> tuple[HolidayInfo, ...]: ...


class HolidayInfo(Protocol):
    id: str
    legal_date: CivilDate
    observed_date: CivilDate


@dataclass(frozen=True, slots=True)
class CalendarContext:
    """Explicit configuration for Gregorian grids and date analyses.

    Version 0.1.0 generates grids for ``proleptic-gregorian`` dates. Julian and
    reform conversions are exposed separately until non-Gregorian grid semantics
    can be represented without ambiguity.
    """

    date_system: str = "proleptic-gregorian"
    week_model: WeekModel = ISO
    holiday_calendar: HolidaySource | None = None
    weekend: frozenset[int] = frozenset({5, 6})

    def __post_init__(self) -> None:
        if self.date_system != "proleptic-gregorian":
            raise ValueError("version 0.1.0 grids support only proleptic-gregorian dates")
        if not self.weekend <= frozenset(range(7)):
            raise ValueError("weekend weekdays must be in 0..6")
