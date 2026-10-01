from jwcalendar_calendrical.analysis.vectors import generate_test_vectors
from jwcalendar_calendrical.holidays.calendar import USFederalHolidayCalendar

for vector in generate_test_vectors(2027, holidays=USFederalHolidayCalendar()):
    print(vector.category.value, vector.date, vector.label)
