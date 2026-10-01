import json

import pytest

from jwcalendar_calendrical import CivilDate, build_month
from jwcalendar_calendrical.analysis.explain import explain_date, explain_year
from jwcalendar_calendrical.analysis.vectors import (
    Discrepancy,
    VectorCategory,
    compare_implementation,
    generate_test_vectors,
)
from jwcalendar_calendrical.business.calendar import BusinessCalendar
from jwcalendar_calendrical.business.intervals import DateInterval, DateSet
from jwcalendar_calendrical.core.errors import SearchLimitExceeded
from jwcalendar_calendrical.export.csv import to_csv
from jwcalendar_calendrical.export.json import to_json, to_jsonl
from jwcalendar_calendrical.grid.fingerprints import month_fingerprint
from jwcalendar_calendrical.holidays.calendar import USFederalHolidayCalendar
from jwcalendar_calendrical.holidays.rules import (
    FixedDate,
    LastWeekday,
    NearestWeekday,
    NthWeekday,
    ObservedRule,
    RelativeToRule,
    UnionRule,
)
from jwcalendar_calendrical.query.predicates import (
    all_of,
    any_of,
    day_of_month_is,
    holiday_is,
    is_business_day,
    is_month_end,
    is_year_boundary,
    month_is,
    not_,
    ordinal_between,
    weekday_is,
)
from jwcalendar_calendrical.query.solver import (
    dates_between,
    next_matching_date,
    previous_matching_date,
)
from jwcalendar_calendrical.systems.julian import JulianDate
from jwcalendar_calendrical.systems.reform import ReformCalendar
from jwcalendar_calendrical.week.models import ISO, WeekModel


def test_holiday_rule_algebra():
    assert FixedDate(2, 29).dates(2027) == ()
    assert NthWeekday(1, 0, 3).dates(2027) == (CivilDate(2027, 1, 18),)
    assert LastWeekday(5, 0).dates(2027) == (CivilDate(2027, 5, 31),)
    assert NearestWeekday(7, 4).dates(2027) == (CivilDate(2027, 7, 5),)
    assert RelativeToRule(FixedDate(1, 1), 1).dates(2027) == (CivilDate(2027, 1, 2),)
    assert ObservedRule(FixedDate(7, 4)).dates(2027) == (CivilDate(2027, 7, 5),)
    assert UnionRule((FixedDate(1, 1), FixedDate(12, 25))).dates(2027) == (
        CivilDate(2027, 1, 1),
        CivilDate(2027, 12, 25),
    )


def test_business_calendar_overrides_and_holidays():
    holiday_calendar = USFederalHolidayCalendar()
    date = CivilDate(2027, 7, 5)
    calendar = BusinessCalendar(
        holidays=holiday_calendar,
        added_working_dates=frozenset({date}),
        excluded_dates=frozenset({CivilDate(2027, 7, 6)}),
    )
    assert calendar.is_business_day(date)
    assert not calendar.is_business_day(CivilDate(2027, 7, 6))
    assert calendar.previous_business_day(CivilDate(2027, 1, 4)) == CivilDate(2026, 12, 31)
    assert calendar.business_days_between(CivilDate(2027, 1, 4), CivilDate(2027, 1, 7)) == 3
    assert calendar.business_days_between(CivilDate(2027, 1, 7), CivilDate(2027, 1, 4)) == -3


def test_interval_set_algebra():
    a = DateSet(
        (
            DateInterval(CivilDate(2027, 1, 1), CivilDate(2027, 1, 3)),
            DateInterval(CivilDate(2027, 1, 4), CivilDate(2027, 1, 5)),
        )
    )
    b = DateSet((DateInterval(CivilDate(2027, 1, 3), CivilDate(2027, 1, 4)),))
    assert len(a.intervals) == 1
    assert a.intersection(b).intervals == (
        DateInterval(CivilDate(2027, 1, 3), CivilDate(2027, 1, 4)),
    )
    assert tuple(a.difference(b).dates()) == tuple(CivilDate(2027, 1, day) for day in (1, 2, 5))
    assert a.union(b).contains(CivilDate(2027, 1, 4))


def test_predicate_composition_and_bounded_search():
    first = CivilDate(2027, 1, 1)
    friday13 = all_of(weekday_is(4), day_of_month_is(13))
    assert next_matching_date(first, friday13) == CivilDate(2027, 8, 13)
    assert previous_matching_date(CivilDate(2027, 8, 31), friday13) == CivilDate(2027, 8, 13)
    assert any_of(month_is(1), month_is(2))(first)
    assert not_(month_is(2))(first)
    assert ordinal_between(1, 1)(first)
    assert is_year_boundary()(first)
    assert not is_month_end()(first)
    assert holiday_is(USFederalHolidayCalendar(), "new_years_day")(first)
    assert is_business_day(BusinessCalendar())(first)
    assert list(dates_between(first, first.add_days(2), weekday_is(4))) == [first]
    with pytest.raises(SearchLimitExceeded):
        next_matching_date(first, month_is(2), max_days=1)
    with pytest.raises(SearchLimitExceeded):
        list(dates_between(first, first.add_days(5), month_is(2), max_days=2))


def test_vectors_reform_business_and_differential():
    reform = ReformCalendar(JulianDate(1582, 10, 4), CivilDate(1582, 10, 15))
    vectors = generate_test_vectors(
        1582,
        reform=reform,
        holidays=USFederalHolidayCalendar(),
        business_calendar=BusinessCalendar(),
    )
    assert any(v.category == VectorCategory.REFORM_GAP for v in vectors)
    assert any(v.category == VectorCategory.BUSINESS_DAY_BOUNDARY for v in vectors)
    assert any(v.category == VectorCategory.GREGORIAN_JULIAN for v in vectors)
    discrepancies = compare_implementation(
        lambda d: d.weekday(), vectors[:4], lambda d: (d.weekday() + 1) % 7
    )
    assert len(discrepancies) == 4
    assert isinstance(discrepancies[0], Discrepancy)


def test_explanations_and_exports():
    date = CivilDate(2027, 1, 1)
    explanation = explain_date(date, holidays=USFederalHolidayCalendar())
    year = explain_year(2027, holidays=USFederalHolidayCalendar(), model=ISO)
    assert explanation.month_grid_row == 0
    assert explanation.month_grid_column == 4
    assert year.days == 365
    rendered = to_json(explanation)
    assert json.loads(rendered)["gregorian"] == "2027-01-01"
    assert json.loads(to_jsonl([explanation]))["fixed_day"] == explanation.fixed_day
    csv_text = to_csv([explanation])
    assert "2027-01-01" in csv_text


def test_early_year_grid_and_context_errors():
    grid = build_month(1, 1, fixed_rows=6)
    assert grid.row_count == 6
    assert any(cell.date is None for cell in grid.rows[0])
    with pytest.raises(ValueError):
        build_month(2027, 1, fixed_rows=4)
    with pytest.raises(ValueError):
        build_month(2027, 1, fixed_rows=7)
    assert month_fingerprint(2027, 1, ISO)["sha256"]
    with pytest.raises(ValueError):
        explain_date(CivilDate(1, 1, 1), model=WeekModel(6, 7))


def test_cli_returns_machine_output(capsys):
    from jwcalendar_calendrical.cli.main import main

    assert main(["iso-week", "2027-01-01"]) == 0
    assert '"week": 53' in capsys.readouterr().out
    assert main(["test-vectors", "2027", "--format", "csv"]) == 0
    assert "category" in capsys.readouterr().out
