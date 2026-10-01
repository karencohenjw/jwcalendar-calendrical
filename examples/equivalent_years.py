from jwcalendar_calendrical.analysis.equivalence import find_equivalent_years
from jwcalendar_calendrical.week.models import ISO

print(find_equivalent_years(2027, 1900, 2200, week_model=ISO))
