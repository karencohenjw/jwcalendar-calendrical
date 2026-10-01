"""The ``jwcal`` command-line interface."""

from __future__ import annotations

import argparse
import sys

from ..analysis.boundaries import scan_boundaries
from ..analysis.equivalence import find_equivalent_years
from ..analysis.explain import explain_date, explain_year
from ..analysis.vectors import generate_test_vectors
from ..core.civil import CivilDate
from ..export.csv import to_csv
from ..export.json import to_json, to_jsonl
from ..grid.fingerprints import month_fingerprint, year_fingerprint
from ..grid.month import build_month
from ..holidays.calendar import USFederalHolidayCalendar
from ..systems.gregorian import to_ordinal_date
from ..systems.iso_week import to_iso_week_date
from ..systems.julian import gregorian_to_julian_calendar
from ..week.models import ISO, MONDAY_FIRST, SUNDAY_FIRST, WeekModel


def _date(value: str) -> CivilDate:
    try:
        y, m, d = (int(x) for x in value.split("-"))
        return CivilDate(y, m, d)
    except Exception as exc:
        raise argparse.ArgumentTypeError("date must be a valid YYYY-MM-DD") from exc


def _render_month(year: int, month: int, model: WeekModel) -> str:
    grid = build_month(year, month, week_model=model)
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    start = model.first_weekday
    out = [f"{year:04d}-{month:02d}", " ".join(names[(start + i) % 7] for i in range(7))]
    for row in grid.rows:
        out.append(
            " ".join(
                f"{c.date.day:2d}"
                if c.in_month and c.date
                else (f"({c.date.day:02d})" if c.date else "  ")
                for c in row
            )
        )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jwcal", description="Exact civil calendar computation and QA tools"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    month = sub.add_parser("month")
    month.add_argument("year", type=int)
    month.add_argument("month", type=int)
    month.add_argument("--week-start", choices=["monday", "sunday"], default="sunday")
    month.add_argument("--json", action="store_true")
    year = sub.add_parser("year")
    year.add_argument("year", type=int)
    year.add_argument("--json", action="store_true")
    exp = sub.add_parser("explain")
    exp.add_argument("date", type=_date)
    exp.add_argument("--json", action="store_true")
    ordinal = sub.add_parser("ordinal")
    ordinal.add_argument("date", type=_date)
    ordinal.add_argument("--json", action="store_true")
    iso = sub.add_parser("iso-week")
    iso.add_argument("date", type=_date)
    iso.add_argument("--json", action="store_true")
    conv = sub.add_parser("convert")
    conv.add_argument("date", type=_date)
    conv.add_argument("--to", choices=["julian-calendar"], required=True)
    holidays = sub.add_parser("holidays")
    holidays.add_argument("year", type=int)
    holidays.add_argument("--calendar", choices=["us-federal"], default="us-federal")
    holidays.add_argument("--json", action="store_true")
    equivalent = sub.add_parser("equivalent-years")
    equivalent.add_argument("year", type=int)
    equivalent.add_argument("--from", dest="start", type=int, default=1900)
    equivalent.add_argument("--to", dest="end", type=int, default=2200)
    equivalent.add_argument("--json", action="store_true")
    boundary = sub.add_parser("boundaries")
    boundary.add_argument("year", type=int)
    boundary.add_argument("--json", action="store_true")
    vectors = sub.add_parser("test-vectors")
    vectors.add_argument("year", type=int)
    vectors.add_argument("--format", choices=["json", "jsonl", "csv"], default="json")
    fingerprint = sub.add_parser("fingerprint")
    fingerprint.add_argument("kind", choices=["month", "year"])
    fingerprint.add_argument("year", type=int)
    fingerprint.add_argument("month", type=int, nargs="?")
    fingerprint.add_argument("--week-start", choices=["monday", "sunday"], default="sunday")
    args = parser.parse_args(argv)
    model: WeekModel = (
        MONDAY_FIRST if getattr(args, "week_start", "sunday") == "monday" else SUNDAY_FIRST
    )
    output: object
    if args.command == "month":
        if args.json:
            output = build_month(args.year, args.month, week_model=model)
        else:
            print(_render_month(args.year, args.month, model))
            return 0
    elif args.command == "year":
        output = explain_year(args.year, holidays=USFederalHolidayCalendar())
    elif args.command == "explain":
        output = explain_date(args.date, holidays=USFederalHolidayCalendar())
    elif args.command == "ordinal":
        output = {"year": to_ordinal_date(args.date)[0], "day": to_ordinal_date(args.date)[1]}
    elif args.command == "iso-week":
        output = {
            "date": str(args.date),
            "iso_week_year": to_iso_week_date(args.date)[0],
            "week": to_iso_week_date(args.date)[1],
            "weekday": to_iso_week_date(args.date)[2],
        }
    elif args.command == "convert":
        output = {
            "gregorian": str(args.date),
            "julian_calendar": str(gregorian_to_julian_calendar(args.date)),
        }
    elif args.command == "holidays":
        output = USFederalHolidayCalendar().occurrences(args.year)
    elif args.command == "equivalent-years":
        output = find_equivalent_years(args.year, args.start, args.end, week_model=ISO)
    elif args.command == "boundaries":
        output = scan_boundaries(args.year, holidays=USFederalHolidayCalendar())
    elif args.command == "test-vectors":
        rows = generate_test_vectors(args.year, holidays=USFederalHolidayCalendar())
        text = (
            to_jsonl(rows)
            if args.format == "jsonl"
            else to_csv(rows)
            if args.format == "csv"
            else to_json(rows)
        )
        print(text, end="\n" if not text.endswith("\n") else "")
        return 0
    elif args.command == "fingerprint":
        if args.kind == "month":
            if args.month is None:
                parser.error("fingerprint month requires MONTH")
            output = month_fingerprint(args.year, args.month, model)
        else:
            output = year_fingerprint(args.year, model)
    else:
        parser.error("unsupported command")
        return 2
    print(to_json(output) if getattr(args, "json", False) else to_json(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
