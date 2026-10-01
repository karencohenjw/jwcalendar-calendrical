"""Holiday calendar protocols and US federal holiday rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..core.civil import CivilDate
from .rules import FixedDate, HolidayRule, LastWeekday, NearestWeekday, NthWeekday

US_FEDERAL_HOLIDAY_SOURCE = "https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/"


@dataclass(frozen=True, slots=True)
class HolidayOccurrence:
    id: str
    name: str
    legal_date: CivilDate
    observed_date: CivilDate

    @property
    def is_observed_on_different_date(self) -> bool:
        return self.legal_date != self.observed_date


class HolidayCalendar(Protocol):
    def occurrences(self, year: int) -> tuple[HolidayOccurrence, ...]: ...
    def on(self, date: CivilDate) -> tuple[HolidayOccurrence, ...]: ...


@dataclass(frozen=True, slots=True)
class USFederalHolidayCalendar:
    """US federal holidays under current nationwide rules; starts Juneteenth in 2021."""

    def occurrences(self, year: int) -> tuple[HolidayOccurrence, ...]:
        if year < 1:
            raise ValueError("year must be >= 1")
        specs: list[tuple[str, str, HolidayRule]] = [
            ("new_years_day", "New Year's Day", NearestWeekday(1, 1)),
            ("mlk_day", "Birthday of Martin Luther King, Jr.", NthWeekday(1, 0, 3)),
            ("washington_birthday", "Washington's Birthday", NthWeekday(2, 0, 3)),
            ("memorial_day", "Memorial Day", LastWeekday(5, 0)),
            ("independence_day", "Independence Day", NearestWeekday(7, 4)),
            ("labor_day", "Labor Day", NthWeekday(9, 0, 1)),
            ("columbus_day", "Columbus Day", NthWeekday(10, 0, 2)),
            ("veterans_day", "Veterans Day", NearestWeekday(11, 11)),
            ("thanksgiving_day", "Thanksgiving Day", NthWeekday(11, 3, 4)),
            ("christmas_day", "Christmas Day", NearestWeekday(12, 25)),
        ]
        out = [
            HolidayOccurrence(i, n, rule.dates(year)[0], rule.dates(year)[0])
            for i, n, rule in specs
        ]
        if year >= 2021:
            rule = NearestWeekday(6, 19)
            d = rule.dates(year)[0]
            out.append(
                HolidayOccurrence("juneteenth", "Juneteenth National Independence Day", d, d)
            )
        # Retain the statutory date as legal_date, separate from weekday observance.
        legal = {
            "new_years_day": FixedDate(1, 1),
            "independence_day": FixedDate(7, 4),
            "veterans_day": FixedDate(11, 11),
            "christmas_day": FixedDate(12, 25),
            "juneteenth": FixedDate(6, 19),
        }
        corrected = []
        for occ in out:
            legal_date = legal[occ.id].dates(year)[0] if occ.id in legal else occ.legal_date
            observed_rule = (
                NearestWeekday(legal_date.month, legal_date.day) if occ.id in legal else None
            )
            observed = observed_rule.dates(year)[0] if observed_rule else legal_date
            corrected.append(HolidayOccurrence(occ.id, occ.name, legal_date, observed))
        return tuple(sorted(corrected, key=lambda o: (o.observed_date, o.id)))

    def on(self, date: CivilDate) -> tuple[HolidayOccurrence, ...]:
        years = {date.year}
        if date.year > 1:
            years.add(date.year - 1)
        years.add(date.year + 1)
        return tuple(
            x
            for year in sorted(years)
            for x in self.occurrences(year)
            if x.legal_date == date or x.observed_date == date
        )
