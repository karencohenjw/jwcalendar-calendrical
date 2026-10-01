from jwcalendar_calendrical import CivilDate, JulianDate
from jwcalendar_calendrical.systems.iso_week import (
    from_iso_week_date,
    to_iso_week_date,
    weeks_in_iso_year,
)
from jwcalendar_calendrical.systems.julian import (
    fixed_to_julian,
    from_julian_day_number,
    gregorian_to_julian_calendar,
    julian_calendar_to_gregorian,
    julian_to_fixed,
    to_julian_day_number,
)


def test_julian_calendar_round_trip_including_gregorian_century():
    for d in (CivilDate(1900, 3, 1), CivilDate(2000, 2, 29), CivilDate(2027, 1, 1)):
        julian = gregorian_to_julian_calendar(d)
        assert julian_calendar_to_gregorian(julian) == d
    assert JulianDate(1900, 2, 29).day == 29
    assert fixed_to_julian(julian_to_fixed(JulianDate(1900, 2, 29))) == JulianDate(1900, 2, 29)


def test_iso_week_boundary_round_trip():
    for d in (
        CivilDate(2021, 1, 1),
        CivilDate(2021, 1, 4),
        CivilDate(2027, 12, 31),
        CivilDate(2000, 1, 1),
    ):
        y, w, wd = to_iso_week_date(d)
        assert from_iso_week_date(y, w, wd) == d
    assert weeks_in_iso_year(2020) == 53
    assert weeks_in_iso_year(2021) == 52
    from datetime import date

    for year in range(1900, 2401):
        assert weeks_in_iso_year(year) == date(year, 12, 28).isocalendar().week


def test_julian_day_number_is_distinct_and_round_trips():
    date = CivilDate(2000, 1, 1)
    assert to_julian_day_number(date) == 2451545
    assert to_julian_day_number(date, at_noon=False) == 2451544.5
    assert from_julian_day_number(2451545) == date
