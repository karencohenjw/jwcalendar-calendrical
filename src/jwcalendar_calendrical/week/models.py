"""Immutable conventions for application-specific week numbering."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WeekModel:
    """A week convention: Monday=0..Sunday=6 and minimum first-week days 1..7."""

    first_weekday: int = 0
    minimal_days_in_first_week: int = 4
    name: str = "custom"

    def __post_init__(self) -> None:
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (self.first_weekday, self.minimal_days_in_first_week)
        ):
            raise ValueError("week model numeric fields must be integers")
        if not 0 <= self.first_weekday <= 6:
            raise ValueError("first_weekday must be in 0..6")
        if not 1 <= self.minimal_days_in_first_week <= 7:
            raise ValueError("minimal_days_in_first_week must be in 1..7")


ISO = WeekModel(0, 4, "ISO")
MONDAY_FIRST = WeekModel(0, 1, "Monday-first")
SUNDAY_FIRST = WeekModel(6, 1, "Sunday-first")
