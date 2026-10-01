"""Week-year and week-number calculations for arbitrary week models."""

from __future__ import annotations

from ..core.civil import CivilDate
from ..systems.gregorian import fixed_to_gregorian, gregorian_to_fixed
from .models import ISO, WeekModel


def _week1_start(year: int, model: WeekModel) -> int:
    if year < 1:
        raise ValueError("week-year 0 is outside the supported positive-year model")
    jan1 = gregorian_to_fixed(CivilDate(year, 1, 1))
    before = (jan1 - 1 - model.first_weekday) % 7
    start = jan1 - before
    days_in_year = 7 - before
    return start if days_in_year >= model.minimal_days_in_first_week else start + 7


def week_year(date: CivilDate, model: WeekModel = ISO) -> int:
    """Return the week-year under ``model``."""
    fixed = gregorian_to_fixed(date)
    if fixed < _week1_start(date.year, model):
        if date.year == 1:
            raise ValueError("week model assigns this date to unsupported week-year 0")
        return date.year - 1
    if fixed >= _week1_start(date.year + 1, model):
        return date.year + 1
    return date.year


def week_of_year(date: CivilDate, model: WeekModel = ISO) -> int:
    """Return a one-based week number under ``model``."""
    wy = week_year(date, model)
    return (gregorian_to_fixed(date) - _week1_start(wy, model)) // 7 + 1


def weeks_in_year(year: int, model: WeekModel = ISO) -> int:
    """Return the number of whole weeks assigned to a week-year."""
    if year < 1:
        raise ValueError("year must be >= 1")
    return (_week1_start(year + 1, model) - _week1_start(year, model)) // 7


def week_start(date: CivilDate, model: WeekModel = ISO) -> CivilDate:
    """Return the first day of the week containing ``date``."""
    fixed = gregorian_to_fixed(date)
    delta = (date.weekday() - model.first_weekday) % 7
    return fixed_to_gregorian(fixed - delta)
