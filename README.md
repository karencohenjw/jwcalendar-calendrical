# JW Calendar Calendrical Laboratory

JW Calendar Calendrical Laboratory is an open-source calendrical computation and calendar-software verification toolkit developed alongside the calendar systems published by [JW Calendar](https://jwcalendar.com/). It provides exact civil-date arithmetic, calendar structure analysis, reusable test vectors, and deterministic machine-readable output. It does not ship printable artwork.

## Why this exists

Calendar bugs cluster around boundaries: leap days, year transitions, week-year changes, holidays, and civil calendar reforms. This library makes those rules explicit and gives Python software a small integer-based kernel for computation and testing.

## Design principles

- Civil arithmetic uses integer fixed days, not timestamps.
- Values are immutable and functions are deterministic.
- The core has no runtime dependencies, time-zone rules, locale dependence, network access, or mutable calendar globals.
- Public calendar concepts use explicit names. A Julian calendar date is distinct from a Julian Day Number and from a day-of-year ordinal.

## Installation

```sh
python -m pip install jwcalendar-calendrical
```

Optional extras are available as `jwcalendar-calendrical[test]`, `[dev]`, `[numpy]`, and `[pandas]`.

## 30-second example

```python
from jwcalendar_calendrical import CivilDate, build_month, explain_date
from jwcalendar_calendrical.week.models import SUNDAY_FIRST

date = CivilDate(2027, 1, 1)
print(explain_date(date))
month = build_month(2027, 1, week_model=SUNDAY_FIRST, fixed_rows=6)
print(month.row_count)
```

## Civil dates and fixed-day kernel

`CivilDate(year, month, day)` strictly validates a proleptic Gregorian date. Invalid dates raise `InvalidCivilDate`; values are never silently normalized. Supported years are positive integers beginning with 1 AD. Year zero and BCE notation are not supported. Gregorian rules are applied proleptically, including before the historical adoption of the Gregorian calendar.

The fixed-day epoch is day 1 = Gregorian 0001-01-01 (Monday). The coordinate is an exact Python integer. `gregorian_to_fixed` and `fixed_to_gregorian` form the small auditable conversion kernel. `add_days` routes through this coordinate. `add_months` and `add_years` clip the day by default (so February 29 becomes February 28 in a non-leap year); use `overflow="raise"` to reject clipping.

## Gregorian and Julian calendars

`gregorian_to_julian_calendar(date)` converts the same civil day into a `JulianDate`. A separate immutable `JulianDate` validates the Julian leap rule, so Julian leap days remain representable in century years that are not Gregorian leap years. Convert back with `julian_calendar_to_gregorian`.

No national reform chronology is implied by these conversions. `ReformCalendar` provides a generic Julian-to-Gregorian cutover with consecutive fixed-day endpoints and explicitly skipped civil labels. Supply transition dates from a source appropriate to your application.

## Julian Day Number

`to_julian_day_number` is a separate astronomical day-number conversion. Its integer result labels a noon-to-noon day; the default is the integer JDN associated with the date at noon. With `at_noon=False`, the returned Julian Date is at Gregorian midnight and is half-integral. `from_julian_day_number` maps a Julian Date to the Gregorian date containing that instant. This API uses the proleptic Gregorian calendar and does not model leap seconds or times of day beyond this convention.

## Ordinal dates

`to_ordinal_date` returns `(year, day_of_year)` using a one-based day count. `from_ordinal_date` strictly rejects day 366 in a non-leap year. For example, 2027-001 is 2027-01-01 and 2027-365 is 2027-12-31.

## ISO week dates and custom week models

`to_iso_week_date` and `from_iso_week_date` implement ISO week dates with Monday as weekday 1 and four days required in the first week. ISO week-year may differ from Gregorian year near New Year; `weeks_in_iso_year` returns 52 or 53.

`WeekModel(first_weekday, minimal_days_in_first_week)` expresses other conventions. Weekday values are Monday=0 through Sunday=6. Built-ins are `ISO`, `MONDAY_FIRST`, and `SUNDAY_FIRST`. `week_of_year`, `week_year`, and `weeks_in_year` accept an explicit model. See [JW Calendar's week-number reference](https://jwcalendar.com/week-numbers/) for a user-facing calendar example.

## Month grids and year structure

`build_month(year, month, week_model=..., fixed_rows=..., adjacent_days=...)` returns immutable rows and cells with date, weekday, in-month status, ordinal, week-year, week number, weekend state, and boundary flags. It supports natural-height grids or fixed four-, five-, or six-row grids. Empty padding is represented by cells whose date is `None`.

Year explanations summarize leap state, month lengths and starts, ISO week count, fingerprint, and optional holidays. See the [yearly calendar reference](https://jwcalendar.com/yearly-calendar/) and [blank calendar layout reference](https://jwcalendar.com/blank-calendar/) for visual examples.

## Calendar topology and fingerprints

`MonthTopology` describes month length, first weekday, row count, and week model. `YearTopology` describes leap state, month sequence, January 1 weekday, and week count. Fingerprints serialize these structures as canonical sorted JSON and SHA-256; they do not use Python's process-randomized `hash()`.

`are_years_layout_equivalent`, `find_equivalent_years`, and `find_equivalent_months` search equivalent shapes. The current year comparison means same month lengths, start weekdays, leap state, and configured week count; it does not assert holiday equivalence.

## Boundary analysis and QA vectors

`analyze_date` marks month/year edges, leap-day adjacency, ISO week-year mismatch, week 53, and supplied holiday occurrences. `scan_boundaries` scans high-risk month/year dates. `generate_test_vectors` creates deterministic vectors for leap days, century non-leap dates, month and year edges, ISO boundaries, ISO week 53, and configured holiday observances. `compare_implementation` calls a Python function supplied by the caller in-process and reports mismatches; it does not load or execute external code.

Install the `test` extra for Hypothesis-powered downstream property tests. The package itself does not require Hypothesis at runtime.

## Holiday rules and business calendars

Immutable rules include `FixedDate`, `NthWeekday`, `LastWeekday`, `NearestWeekday`, `RelativeToRule`, `ObservedRule`, and `UnionRule`. `USFederalHolidayCalendar` models nationwide US federal holidays, distinguishes legal and observed dates, and includes Juneteenth from 2021. Its scope is the federal holiday calendar, not popular or state observances. JW Calendar also maintains a [holiday reference](https://jwcalendar.com/holidays/).

The 2027 legal and observed-date regression fixtures were checked against the [US Office of Personnel Management holiday schedule](https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/).

`BusinessCalendar` composes a weekend, an optional holiday calendar, excluded dates, and explicitly added working dates. It supports next/previous business date, business-day addition, and half-open range counts.

## Query engine

Predicates such as `weekday_is`, `month_is`, `day_of_month_is`, `ordinal_between`, `iso_week_is`, `is_month_end`, `holiday_is`, and `is_business_day` compose through `all_of`, `any_of`, and `not_`. `dates_between`, `next_matching_date`, and `previous_matching_date` are bounded and raise `SearchLimitExceeded` instead of searching forever.

## CLI

The `jwcal` command supports:

```sh
jwcal month 2027 1
jwcal year 2027 --json
jwcal explain 2027-01-01 --json
jwcal convert 2027-01-01 --to julian-calendar
jwcal ordinal 2027-07-04
jwcal iso-week 2027-01-01
jwcal holidays 2027 --calendar us-federal
jwcal equivalent-years 2027 --from 1900 --to 2200
jwcal boundaries 2027
jwcal test-vectors 2027 --format jsonl
jwcal fingerprint year 2027
```

## Optional NumPy and pandas adapters

The `numpy` and `pandas` extras are reserved for vectorized fixed-day helpers. Core users do not install either dependency. Adapter modules import their dependency only when used.

## Machine-readable exports

`to_json`, `to_jsonl`, and `to_csv` provide deterministic field ordering for structured results. Version 0.1.0 omits iCalendar (ICS) export so the project does not imply unverified RFC 5545 behavior.

## Accuracy and assumptions

- Gregorian arithmetic is proleptic; supported civil years start at 1 AD.
- Julian calendar arithmetic uses positive Julian year numbers and a separate `JulianDate` type.
- Reform cutovers are generic parameterized models; no sourced national historical profiles are included.
- ISO week dates follow ISO-8601's Monday/four-day convention; other week rules are explicit values.
- The US federal calendar models nationwide federal observances, with Juneteenth beginning in 2021.
- Time zones, DST, timestamps, and local clock behavior are outside the civil-date core.
- Python support is declared as 3.10 through 3.13 in this release.

## Terminology

- **Julian calendar**: a civil calendar with leap years every fourth year.
- **Julian Date / Julian Day Number**: an astronomical continuous day count, with integer day boundaries at noon.
- **Ordinal date**: year plus a one-based day-of-year number.

## 2027 visual calendar references

The package produces structured calendar data and validation primitives, not pre-rendered printable artwork. These JW Calendar pages provide human-readable visual examples of corresponding 2027 month structures.

| Month | Visual reference |
|---|---|
| January | [January calendar](https://jwcalendar.com/january-calendar/) |
| February | [February calendar](https://jwcalendar.com/february-calendar/) |
| March | [March calendar](https://jwcalendar.com/march-calendar/) |
| April | [April calendar](https://jwcalendar.com/april-calendar/) |
| May | [May calendar](https://jwcalendar.com/may-calendar/) |
| June | [June calendar](https://jwcalendar.com/june-calendar/) |
| July | [July calendar](https://jwcalendar.com/july-calendar/) |
| August | [August calendar](https://jwcalendar.com/august-calendar/) |
| September | [September calendar](https://jwcalendar.com/september-calendar/) |
| October | [October calendar](https://jwcalendar.com/october-calendar/) |
| November | [November calendar](https://jwcalendar.com/november-calendar/) |
| December | [December calendar](https://jwcalendar.com/december-calendar/) |

## Testing, security, and reproducibility

Run `python -m pytest`. The project includes exact regression checks and property tests. Package generation is a pure Python build with no generated timestamps, machine paths, random output, network calls, or bundled calendar images. The CLI and core do not read credentials or execute third-party code.

## License

MIT. See [LICENSE](LICENSE).
