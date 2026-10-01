"""Parameterized Julian-to-Gregorian civil-date reform model."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.civil import CivilDate
from ..core.errors import CalendarGapError, InvalidCivilDate
from .gregorian import fixed_to_gregorian, gregorian_to_fixed
from .julian import JulianDate, fixed_to_julian, julian_to_fixed


@dataclass(frozen=True, slots=True)
class ReformCalendar:
    """A cutover from the Julian calendar to proleptic Gregorian labels.

    The fixed day immediately after ``last_old_style_date`` must be
    ``first_new_style_date``. Label dates between those endpoints are skipped.
    The model intentionally includes no named historical national profiles.
    """

    last_old_style_date: JulianDate
    first_new_style_date: CivilDate

    def __post_init__(self) -> None:
        if julian_to_fixed(self.last_old_style_date) + 1 != gregorian_to_fixed(
            self.first_new_style_date
        ):
            raise ValueError("cutover endpoints must denote consecutive fixed days")
        if (
            self.last_old_style_date.year,
            self.last_old_style_date.month,
            self.last_old_style_date.day,
        ) >= (
            self.first_new_style_date.year,
            self.first_new_style_date.month,
            self.first_new_style_date.day,
        ):
            raise ValueError("first new-style label must follow the last old-style label")

    def is_valid_civil_date(self, date: CivilDate) -> bool:
        label = (date.year, date.month, date.day)
        old = (
            self.last_old_style_date.year,
            self.last_old_style_date.month,
            self.last_old_style_date.day,
        )
        new = (
            self.first_new_style_date.year,
            self.first_new_style_date.month,
            self.first_new_style_date.day,
        )
        return label <= old or label >= new

    def to_fixed(self, date: CivilDate) -> int:
        """Interpret a label in the appropriate side of the reform."""
        if not self.is_valid_civil_date(date):
            raise CalendarGapError(f"{date} is skipped by the calendar reform")
        try:
            if (date.year, date.month, date.day) <= (
                self.last_old_style_date.year,
                self.last_old_style_date.month,
                self.last_old_style_date.day,
            ):
                return julian_to_fixed(JulianDate(date.year, date.month, date.day))
            return gregorian_to_fixed(date)
        except InvalidCivilDate as exc:
            raise CalendarGapError(str(exc)) from exc

    def from_fixed(self, fixed_day: int) -> CivilDate:
        """Return the civil label in force on ``fixed_day``."""
        if fixed_day <= julian_to_fixed(self.last_old_style_date):
            d = fixed_to_julian(fixed_day)
            return CivilDate(d.year, d.month, d.day)
        return fixed_to_gregorian(fixed_day)

    def gap_dates(self) -> tuple[CivilDate, ...]:
        """Return the skipped labels between the cutover endpoints."""
        out: list[CivilDate] = []
        cursor = CivilDate(
            self.last_old_style_date.year,
            self.last_old_style_date.month,
            self.last_old_style_date.day,
        ).add_days(1)
        while cursor < self.first_new_style_date:
            out.append(cursor)
            cursor = cursor.add_days(1)
        return tuple(out)

    def difference_across_reform(self) -> dict[str, int]:
        """Summarize skipped labels and the continuous fixed-day interval."""
        return {"skipped_labels": len(self.gap_dates()), "fixed_day_step": 1}
