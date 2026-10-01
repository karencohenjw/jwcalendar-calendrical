from jwcalendar_calendrical.business.calendar import BusinessCalendar
from jwcalendar_calendrical.core.civil import CivilDate

calendar = BusinessCalendar()
print(calendar.add_business_days(CivilDate(2027, 1, 1), 5))
