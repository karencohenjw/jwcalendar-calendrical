"""Deterministic adversarial date vectors for calendar QA."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from ..core.civil import CivilDate, days_in_month, is_leap_year
from ..holidays.calendar import HolidayCalendar
from ..systems.iso_week import weeks_in_iso_year


class VectorCategory(str, Enum):
    LEAP_DAY = "leap_day"
    CENTURY_NON_LEAP = "century_non_leap"
    YEAR_BOUNDARY = "year_boundary"
    MONTH_BOUNDARY = "month_boundary"
    ISO_WEEK_BOUNDARY = "iso_week_boundary"
    ISO_WEEK_53 = "iso_week_53"
    GREGORIAN_JULIAN = "gregorian_julian"
    REFORM_GAP = "reform_gap"
    HOLIDAY_OBSERVANCE = "holiday_observance"
    BUSINESS_DAY_BOUNDARY = "business_day_boundary"


@dataclass(frozen=True, slots=True)
class TestVector:
    category: VectorCategory
    date: CivilDate
    label: str


class _ReformSource(Protocol):
    def gap_dates(self) -> tuple[CivilDate, ...]: ...


class _BusinessSource(Protocol):
    def is_business_day(self, date: CivilDate) -> bool: ...


class _ReformCalendarSource(Protocol):
    def gap_dates(self) -> tuple[CivilDate, ...]: ...


def generate_test_vectors(
    year: int,
    *,
    holidays: HolidayCalendar | None = None,
    reform: _ReformCalendarSource | None = None,
    business_calendar: _BusinessSource | None = None,
) -> tuple[TestVector, ...]:
    """Generate stable vectors for leap, month/year, week, and holiday boundaries."""
    vectors: list[TestVector] = []
    if is_leap_year(year):
        vectors.append(TestVector(VectorCategory.LEAP_DAY, CivilDate(year, 2, 29), "leap day"))
    if year % 100 == 0 and year % 400 != 0:
        vectors.append(
            TestVector(
                VectorCategory.CENTURY_NON_LEAP, CivilDate(year, 2, 28), "century non-leap edge"
            )
        )
    for d in (CivilDate(year, 1, 1), CivilDate(year, 12, 31)):
        vectors.append(TestVector(VectorCategory.YEAR_BOUNDARY, d, "calendar year boundary"))
    for month in range(1, 13):
        vectors.append(
            TestVector(VectorCategory.MONTH_BOUNDARY, CivilDate(year, month, 1), "month start")
        )
        vectors.append(
            TestVector(
                VectorCategory.MONTH_BOUNDARY,
                CivilDate(year, month, days_in_month(year, month)),
                "month end",
            )
        )
    for d in (
        CivilDate(year, 1, 1),
        CivilDate(year, 1, 4),
        CivilDate(year, 12, 28),
        CivilDate(year, 12, 31),
    ):
        vectors.append(TestVector(VectorCategory.ISO_WEEK_BOUNDARY, d, "ISO week-year edge"))
    if weeks_in_iso_year(year) == 53:
        vectors.append(
            TestVector(VectorCategory.ISO_WEEK_53, CivilDate(year, 12, 31), "ISO week 53")
        )
    vectors.append(
        TestVector(
            VectorCategory.GREGORIAN_JULIAN,
            CivilDate(year, 1, 1),
            "same fixed day in Gregorian and Julian civil calendars",
        )
    )
    if reform:
        vectors.extend(
            TestVector(VectorCategory.REFORM_GAP, date, "skipped reform label")
            for date in reform.gap_dates()
            if date.year == year
        )
    if holidays:
        for occ in holidays.occurrences(year):
            if occ.legal_date != occ.observed_date:
                vectors.append(
                    TestVector(VectorCategory.HOLIDAY_OBSERVANCE, occ.observed_date, occ.id)
                )
    if business_calendar:
        for month in range(1, 13):
            for day in range(1, days_in_month(year, month) + 1):
                date = CivilDate(year, month, day)
                current = business_calendar.is_business_day(date)
                try:
                    previous = business_calendar.is_business_day(date.add_days(-1))
                except ValueError:
                    previous = current
                try:
                    following = business_calendar.is_business_day(date.add_days(1))
                except ValueError:
                    following = current
                if current != previous or current != following:
                    vectors.append(
                        TestVector(
                            VectorCategory.BUSINESS_DAY_BOUNDARY,
                            date,
                            "weekend or holiday boundary",
                        )
                    )
    return tuple(sorted(set(vectors), key=lambda v: (v.date, v.category.value, v.label)))


@dataclass(frozen=True, slots=True)
class Discrepancy:
    date: CivilDate
    expected: object
    actual: object
    label: str


def compare_implementation(
    function: Callable[[CivilDate], object],
    vectors: Iterable[TestVector],
    expected: Callable[[CivilDate], object],
) -> tuple[Discrepancy, ...]:
    """Call a user-supplied in-process function and collect value mismatches."""
    out = []
    for vector in vectors:
        want = expected(vector.date)
        got = function(vector.date)
        if got != want:
            out.append(Discrepancy(vector.date, want, got, vector.label))
    return tuple(out)
