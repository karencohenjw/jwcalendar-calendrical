"""Domain exceptions used by the calendrical API."""


class CalendarError(Exception):
    """Base class for calendar-domain errors."""


class InvalidCivilDate(CalendarError, ValueError):
    """A year, month, and day do not identify a valid date."""


class InvalidOrdinalDate(CalendarError, ValueError):
    """An ordinal day is outside the selected year's range."""


class InvalidISOWeekDate(CalendarError, ValueError):
    """An ISO week date is outside its valid week-year range."""


class CalendarGapError(CalendarError, ValueError):
    """A reform calendar date lies in a civil-date cutover gap."""


class SearchLimitExceeded(CalendarError):
    """A bounded date query did not find a match before its limit."""


class UnsupportedCalendarOperation(CalendarError, NotImplementedError):
    """A calendar system does not implement the requested operation."""


class InvalidHolidayRule(CalendarError, ValueError):
    """A holiday rule has invalid parameters."""
