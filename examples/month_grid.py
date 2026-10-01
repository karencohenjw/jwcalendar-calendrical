from jwcalendar_calendrical import build_month
from jwcalendar_calendrical.week.models import SUNDAY_FIRST

grid = build_month(2027, 1, week_model=SUNDAY_FIRST, fixed_rows=6)
for row in grid.rows:
    print(" ".join(f"{cell.date.day:2d}" if cell.date and cell.in_month else "  " for cell in row))
