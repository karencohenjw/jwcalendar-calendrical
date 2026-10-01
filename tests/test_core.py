from datetime import date, timedelta

import pytest

from jwcalendar_calendrical import CivilDate, fixed_to_gregorian, gregorian_to_fixed
from jwcalendar_calendrical.core.errors import InvalidCivilDate, InvalidOrdinalDate
from jwcalendar_calendrical.systems.gregorian import day_of_year, from_ordinal_date, to_ordinal_date


def test_strict_dates_and_month_overflow():
    with pytest.raises(InvalidCivilDate):
        CivilDate(2027, 2, 30)
    assert CivilDate(2024, 2, 29).add_years(1) == CivilDate(2025, 2, 28)
    with pytest.raises(InvalidCivilDate):
        CivilDate(2024, 2, 29).add_years(1, overflow="raise")


@pytest.mark.parametrize("year,leap", [(1900, False), (2000, True), (2100, False), (2400, True)])
def test_century_rules(year, leap):
    from jwcalendar_calendrical import is_leap_year

    assert is_leap_year(year) is leap


def test_fixed_roundtrip_and_datetime_differential():
    for year in range(1, 1200):
        for month in (1, 2, 3, 6, 9, 12):
            for day in (1, 15):
                d = CivilDate(year, month, day)
                assert fixed_to_gregorian(gregorian_to_fixed(d)) == d
                if year >= 1:
                    std = date(year, month, day)
                    assert d.weekday() == std.weekday()
                    assert day_of_year(d) == std.timetuple().tm_yday
                    later = std + timedelta(days=17)
                    assert d.add_days(17) == CivilDate(later.year, later.month, later.day)


def test_ordinal_strict_round_trip():
    for year in (1, 4, 1900, 2000, 2027, 2400):
        total = 366 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 365
        for ordinal in (1, total // 2, total):
            assert to_ordinal_date(from_ordinal_date(year, ordinal)) == (year, ordinal)
    with pytest.raises(InvalidOrdinalDate):
        from_ordinal_date(2027, 366)


def test_large_year_roundtrip():
    for year in (10_000, 100_000, 10**8):
        d = CivilDate(year, 12, 31)
        assert fixed_to_gregorian(gregorian_to_fixed(d)) == d
