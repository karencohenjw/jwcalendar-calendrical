"""Business-day arithmetic over explicit weekend and holiday policies."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.civil import CivilDate
from ..holidays.calendar import HolidayCalendar


@dataclass(frozen=True, slots=True)
class BusinessCalendar:
    weekend: frozenset[int] = frozenset({5, 6})
    holidays: HolidayCalendar | None = None
    excluded_dates: frozenset[CivilDate] = frozenset()
    added_working_dates: frozenset[CivilDate] = frozenset()

    def __post_init__(self) -> None:
        if not self.weekend <= frozenset(range(7)):
            raise ValueError("weekend weekdays must be 0..6")

    def is_business_day(self, date: CivilDate) -> bool:
        if date in self.added_working_dates:
            return True
        if date in self.excluded_dates or date.weekday() in self.weekend:
            return False
        return not (self.holidays and self.holidays.on(date))

    def next_business_day(self, date: CivilDate, *, include_date: bool = False) -> CivilDate:
        cur = date if include_date else date.add_days(1)
        for _ in range(3700):
            if self.is_business_day(cur):
                return cur
            cur = cur.add_days(1)
        raise RuntimeError("no business date found within ten years")

    def previous_business_day(self, date: CivilDate, *, include_date: bool = False) -> CivilDate:
        cur = date if include_date else date.add_days(-1)
        for _ in range(3700):
            if self.is_business_day(cur):
                return cur
            cur = cur.add_days(-1)
        raise RuntimeError("no business date found within ten years")

    def add_business_days(self, date: CivilDate, amount: int) -> CivilDate:
        if amount == 0:
            return date
        step = 1 if amount > 0 else -1
        left = abs(amount)
        cur = date
        while left:
            cur = cur.add_days(step)
            if self.is_business_day(cur):
                left -= 1
        return cur

    def business_days_between(self, start: CivilDate, end: CivilDate) -> int:
        """Count business dates in [start, end), supporting either direction."""
        if start == end:
            return 0
        step = 1 if end > start else -1
        count = 0
        cur = start
        while cur != end:
            if step > 0 and self.is_business_day(cur):
                count += 1
            if step < 0 and self.is_business_day(cur.add_days(-1)):
                count -= 1
            cur = cur.add_days(step)
        return count
