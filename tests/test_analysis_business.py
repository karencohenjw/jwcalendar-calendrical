from jwcalendar_calendrical import CivilDate
from jwcalendar_calendrical.analysis.boundaries import analyze_date, scan_boundaries
from jwcalendar_calendrical.analysis.vectors import generate_test_vectors
from jwcalendar_calendrical.business.calendar import BusinessCalendar
from jwcalendar_calendrical.business.intervals import DateInterval, DateSet
from jwcalendar_calendrical.core.errors import CalendarGapError
from jwcalendar_calendrical.holidays.calendar import USFederalHolidayCalendar
from jwcalendar_calendrical.query.predicates import all_of, day_of_month_is, weekday_is
from jwcalendar_calendrical.query.solver import dates_between
from jwcalendar_calendrical.systems.julian import JulianDate
from jwcalendar_calendrical.systems.reform import ReformCalendar


def test_reform_gap():
    reform = ReformCalendar(JulianDate(1582, 10, 4), CivilDate(1582, 10, 15))
    assert len(reform.gap_dates()) == 10
    assert reform.from_fixed(reform.to_fixed(CivilDate(1582, 10, 15))) == CivilDate(1582, 10, 15)
    try:
        reform.to_fixed(CivilDate(1582, 10, 10))
    except CalendarGapError:
        pass
    else:
        raise AssertionError("gap label should be rejected")


def test_business_days_intervals_and_queries():
    cal = BusinessCalendar()
    assert cal.add_business_days(CivilDate(2027, 1, 1), 1) == CivilDate(2027, 1, 4)
    jan = DateSet((DateInterval(CivilDate(2027, 1, 1), CivilDate(2027, 1, 10)),))
    cut = DateSet((DateInterval(CivilDate(2027, 1, 4), CivilDate(2027, 1, 5)),))
    assert not jan.difference(cut).contains(CivilDate(2027, 1, 4))
    matches = list(
        dates_between(
            CivilDate(2027, 1, 1), CivilDate(2027, 1, 31), all_of(weekday_is(4), day_of_month_is(1))
        )
    )
    assert matches == [CivilDate(2027, 1, 1)]


def test_boundary_and_vector_categories():
    assert (
        "year_start"
        in analyze_date(CivilDate(2027, 1, 1), holidays=USFederalHolidayCalendar()).flags
    )
    assert scan_boundaries(2027, holidays=USFederalHolidayCalendar())
    assert generate_test_vectors(2027, holidays=USFederalHolidayCalendar())
