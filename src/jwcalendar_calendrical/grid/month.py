"""Structured calendar month grids."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..core.civil import CivilDate, days_in_month
from ..systems.gregorian import day_of_year
from ..week.calculations import week_of_year, week_year
from ..week.models import SUNDAY_FIRST, WeekModel


class _HolidaySource(Protocol):
    def on(self, date: CivilDate) -> tuple[_HolidayOccurrence, ...]: ...


class _HolidayOccurrence(Protocol):
    id: str


@dataclass(frozen=True, slots=True)
class MonthCell:
    date: CivilDate | None
    row: int
    column: int
    in_month: bool
    weekday: int | None
    ordinal_day: int | None
    week_number: int | None
    week_year: int | None
    weekend: bool
    holiday_ids: tuple[str, ...] = ()
    boundary_flags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MonthGrid:
    year: int
    month: int
    week_model: WeekModel
    rows: tuple[tuple[MonthCell, ...], ...]

    @property
    def row_count(self) -> int:
        return len(self.rows)


def build_month(
    year: int,
    month: int,
    *,
    week_model: WeekModel = SUNDAY_FIRST,
    fixed_rows: int | None = None,
    adjacent_days: bool = True,
    weekend: frozenset[int] = frozenset({5, 6}),
    holidays: _HolidaySource | None = None,
) -> MonthGrid:
    """Build a natural or fixed-row month grid, Monday=0 weekday numbering."""
    if fixed_rows not in (None, 4, 5, 6):
        raise ValueError("fixed_rows must be None, 4, 5, or 6")
    start = CivilDate(year, month, 1)
    leading = (start.weekday() - week_model.first_weekday) % 7
    count = (leading + days_in_month(year, month) + 6) // 7
    rows_count = fixed_rows or count
    if rows_count < count:
        raise ValueError("fixed_rows is too small for this month")
    rows: list[tuple[MonthCell, ...]] = []
    for r in range(rows_count):
        cells = []
        for c in range(7):
            offset = r * 7 + c - leading
            date = None
            if adjacent_days or 0 <= offset < days_in_month(year, month):
                try:
                    date = start.add_days(offset)
                except ValueError:
                    # CivilDate deliberately has no year zero; early padding stays blank.
                    date = None
            in_month = date is not None and date.year == year and date.month == month
            flags = []
            if date and date.day == 1:
                flags.append("month_start")
            if date and date.day == days_in_month(date.year, date.month):
                flags.append("month_end")
            if date and date.month == 1 and date.day == 1:
                flags.append("year_start")
            if date and date.month == 12 and date.day == 31:
                flags.append("year_end")
            cells.append(
                MonthCell(
                    date,
                    r,
                    c,
                    in_month,
                    date.weekday() if date else None,
                    day_of_year(date) if date else None,
                    week_of_year(date, week_model) if date else None,
                    week_year(date, week_model) if date else None,
                    bool(date and date.weekday() in weekend),
                    tuple(
                        str(occurrence.id)
                        for occurrence in (holidays.on(date) if holidays and date else ())
                    ),
                    tuple(flags),
                )
            )
        rows.append(tuple(cells))
    return MonthGrid(year, month, week_model, tuple(rows))
