from jwcalendar_calendrical import CalendarContext, CivilDate, build_month, build_year
from jwcalendar_calendrical.analysis.equivalence import find_equivalent_months
from jwcalendar_calendrical.grid.fingerprints import month_fingerprint, year_fingerprint
from jwcalendar_calendrical.holidays.calendar import USFederalHolidayCalendar
from jwcalendar_calendrical.week.models import ISO, SUNDAY_FIRST


def test_january_2027_grid_and_stable_fingerprint():
    grid = build_month(2027, 1, week_model=SUNDAY_FIRST, fixed_rows=6)
    assert grid.row_count == 6
    assert grid.rows[0][5].date == CivilDate(2027, 1, 1)
    assert month_fingerprint(2027, 1, SUNDAY_FIRST) == month_fingerprint(2038, 1, SUNDAY_FIRST)
    assert year_fingerprint(2027, ISO)["sha256"] == year_fingerprint(2038, ISO)["sha256"]


def test_2027_month_starts_and_lengths():
    from jwcalendar_calendrical import days_in_month

    assert [CivilDate(2027, m, 1).weekday() for m in range(1, 13)] == [
        4,
        0,
        0,
        3,
        5,
        1,
        3,
        6,
        2,
        4,
        0,
        2,
    ]
    assert [days_in_month(2027, m) for m in range(1, 13)] == [
        31,
        28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ]
    for month in range(1, 13):
        grid = build_month(2027, month, week_model=SUNDAY_FIRST)
        assert 4 <= grid.row_count <= 6


def test_us_federal_2027_legal_and_observed_dates():
    occurrences = {o.id: o for o in USFederalHolidayCalendar().occurrences(2027)}
    assert len(occurrences) == 11
    assert occurrences["juneteenth"].legal_date == CivilDate(2027, 6, 19)
    assert occurrences["juneteenth"].observed_date == CivilDate(2027, 6, 18)
    assert occurrences["independence_day"].observed_date == CivilDate(2027, 7, 5)
    assert occurrences["christmas_day"].observed_date == CivilDate(2027, 12, 24)


def test_calendar_context_and_year_grid_holiday_index():
    holidays = USFederalHolidayCalendar()
    year = build_year(
        2027,
        CalendarContext(week_model=SUNDAY_FIRST, holiday_calendar=holidays),
    )
    assert year.days == 365
    assert len(year.months) == 12
    assert any(
        "juneteenth" in cell.holiday_ids
        for row in year.months[5].rows
        for cell in row
        if cell.date == CivilDate(2027, 6, 18)
    )


def test_month_equivalence_search():
    results = find_equivalent_months(2027, 1, 2020, 2040, week_model=SUNDAY_FIRST)
    assert (2038, 1) in results
