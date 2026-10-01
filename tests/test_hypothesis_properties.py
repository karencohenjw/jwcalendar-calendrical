from hypothesis import given, settings

from jwcalendar_calendrical import fixed_to_gregorian, gregorian_to_fixed
from jwcalendar_calendrical.analysis.hypothesis import civil_dates
from jwcalendar_calendrical.systems.gregorian import from_ordinal_date, to_ordinal_date
from jwcalendar_calendrical.systems.iso_week import from_iso_week_date, to_iso_week_date
from jwcalendar_calendrical.systems.julian import (
    fixed_to_julian,
    gregorian_to_julian_calendar,
    julian_calendar_to_gregorian,
    julian_to_fixed,
)


@settings(max_examples=2000, deadline=None)
@given(civil_dates(1, 9999))
def test_core_round_trip_properties(date):
    assert fixed_to_gregorian(gregorian_to_fixed(date)) == date
    assert from_ordinal_date(*to_ordinal_date(date)) == date
    assert from_iso_week_date(*to_iso_week_date(date)) == date
    julian = gregorian_to_julian_calendar(date)
    assert fixed_to_julian(julian_to_fixed(julian)) == julian
    assert julian_calendar_to_gregorian(julian) == date
    assert date.add_days(123).add_days(-123) == date
