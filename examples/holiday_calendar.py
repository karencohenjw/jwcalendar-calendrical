from jwcalendar_calendrical.holidays.calendar import USFederalHolidayCalendar

for occurrence in USFederalHolidayCalendar().occurrences(2027):
    print(occurrence.id, occurrence.legal_date, occurrence.observed_date)
