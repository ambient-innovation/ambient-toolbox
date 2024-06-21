
## Date

### DateHelper

The date helper class provides constants to use when querying for weekdays ("Monday", "Tuesday") with the django ORM.
The assignment from numbers to weekdays is not standarised throughout the different django packages. For example,
in the ``calendar`` extension, Monday equals `0`, in the djang ORM, a Monday is represented by `2`.

To avoid using the integers directly, you can use the constants from this class as follows:

````python
# Just get records where `my_date` is on a Sunday
MyModel.objects.filter(my_date__week_day=DateHelper.ORM_SUNDAY)

# Leave out records where `my_date` is on the weekend
MyModel.objects.exclude(my_date__week_day__in[DateHelper.ORM_SATURDAY, DateHelper.ORM_SUNDAY])
````

### Add months

The function ``add_months(source_date)`` provides a simple way to add any number of months to a given date:

````python
from ambient_toolbox.utils import add_months

new_date = add_months(datetime.date(year=2020, month=9, day=19), 2)
# new_date = datetime.date(2020, 11, 19)
````

You can also use a negative number to subtract months.

### Add days

The function ``add_days(source_date)`` provides a simple way to add any number of months to a given date:

````python
from ambient_toolbox.utils import add_days

new_date = add_days(datetime.date(year=2020, month=9, day=19), 2)
# new_date = datetime.date(2020, 9, 21)
````

You can also use a negative number to subtract days.

### Add minutes

The function ``add_minutes(source_datetime)`` provides a simple way to add any number of months to a given date:

````python
from ambient_toolbox.utils import add_days

new_datetime = add_minutes(datetime.datetime(year=2020, month=9, day=19, hour=8), 60)
# new_datetime = add_minutes.date(2020, 9, 19, 9)
````

You can also use a negative number to subtract minutes.

### Get next month

The function ``get_next_month()`` is a wrapper for ``add_months()`` and will return the current day one month later.

### First day of month

The function ``first_day_of_month(source_date)`` will return the first of month for any given date:

````python
from ambient_toolbox.utils import first_day_of_month

new_date = first_day_of_month(datetime.date(year=2020, month=9, day=19))
# new_date = datetime.date(2020, 9, 1)
````

### Format date to German format

The function ``get_formatted_date_str(source_date)`` will return the string representation in the German format ("d.m.Y"):

````python
from ambient_toolbox.utils import get_formatted_date_str

date_str = get_formatted_date_str(datetime.date(year=2020, month=9, day=19))
# date_str = "19.09.2020"
````

### Create string representation of seconds


The function ``get_time_from_seconds(seconds)`` will create a string representation of any (positive) number of seconds
in the format "HH:mm:ss":

````python
from ambient_toolbox.utils import get_formatted_date_str

time_str = get_time_from_seconds(3661)
# time_str = "01:01:01"

time_str = get_time_from_seconds(65)
# time_str = "00:01:05"
````

### Format datetime objects timezone-aware

The function ``datetime_format(target_datetime, dt_format)`` formats the given datetime according to the given format
with ``strftime`` but takes the django timezone settings into account. If the timeszone cannot be interpreted, a fallback
without the timezone is used:

````python
# settings.py
TIME_ZONE = 'Europe/Berlin'

# my_code.py
source_date = datetime.datetime(year=2020, month=6, day=26, hour=8, tzinfo=pytz.UTC)
datetime_str = datetime_format(source_date, '%d.%m.%Y %H:%M')  # will return '26.06.2020 10:00'
````

### Get start and end dates from calendar week

The function ``get_start_and_end_date_from_calendar_week(year, calendar_week)`` provides a simple way to get the Monday
and Sunday of a given calendar week:

````python
from ambient_toolbox.utils import get_start_and_end_date_from_calendar_week

monday, sunday = get_start_and_end_date_from_calendar_week(2020, 38)
# monday = datetime.date(2020, 09, 14); sunday = datetime.date(2020, 9, 20)
````

### Get next calendar week

The function ``get_next_calendar_week(compare_date)`` will return the the calendar week following the week of the given
``compare_date`` as an integer.

````python
import datetime
from ambient_toolbox.utils import get_next_calendar_week

next_calendar_week = get_next_calendar_week(datetime.date(year=2020, month=9, day=19))
# next_calendar_week = 39
````

### Get next weekday

The function ``next_weekday(given_date, weekday)`` will return a date object of the next weekday following `given_date`.

````python
import calendar
import datetime
from ambient_toolbox.utils import next_weekday

next_friday = next_weekday(datetime.date(year=2020, month=9, day=19), calendar.FRIDAY)
# next_friday = datetime.date(year=2020, month=9, day=25)
````

### Calculate the exact delta between to dates in months

The function ``date_month_delta(start_date, end_date)`` calculates the number of months lying between two dates as
float. So from April 15th to May 1st it's 0.5 months. Attention: The `end_date` will be excluded in the result
(outer border).

````python
import calendar
import datetime
from ambient_toolbox.utils import date_month_delta

months = date_month_delta(datetime.date(year=2020, month=8, day=1), datetime.date(year=2020, month=10, day=1))
# months = 2.0
````

### Get the first and last date of a month

The function ``get_first_and_last_of_month()`` returns the first and last date of a month as a Tuple.
The month is either the current month (if no date_object is passed), or the month of any date that is being passed.
Dates passed need to be datetime.date objects (not datetime.datetime)!

````python
from ambient_toolbox.utils import get_first_and_last_of_month

# Today is 04.04.2022
first_of_month, last_of_month = get_first_and_last_of_month()
# first_of_month = datetime.date(day=1, month=4, year=2022)
# last_of_month = datetime.date(day=30, month=4, year=2022)

# Today is 02.06.2022
first_of_month, last_of_month = get_first_and_last_of_month(datetime(day=16, month=12, year=2022))
# first_of_month = datetime.date(day=1, month=12, year=2022)
# last_of_month = datetime.date(day=31, month=12, year=2022)
````

### Get current date

The function ``tz_today()`` will return the current date as an object. If timezone-awareness is enabled, the date
take it into consideration.

You can optionally use the argument ``str_format``, then the current date will be formatted in the given way and the
function will return a string. Please provide a ``strftime``-compatible value.

````python
from ambient_toolbox.utils import next_weekday

# Here we'll get an object
current_date = tz_today()

# Here we'll get a string
current_date = tz_today('%d.%m.%Y')
````

## Object ownership helper

The function ``log_whodid`` provides a simple way to ensure object ownership is set correctly. Imagine, you have a model
which is derived from ``CommonInfo``:

````python
from ambient_toolbox.models import CommonInfo

class MyModel(CommonInfo):
    pass
````

You can now use the helper in **any place where you have the user object available** to set ``created_by``
and ``lastmodified_by`` like this:

````python
def my_view(request, pk):
    obj = MyModel.objects.get(pk=pk)
    # Let the magic happen
    log_whodid(obj, request.user)
    ...
````
