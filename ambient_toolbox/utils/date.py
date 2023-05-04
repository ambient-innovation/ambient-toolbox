import datetime
from calendar import monthrange
from typing import Tuple, Union

import pytz
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pytz import UnknownTimeZoneError


class DateHelper:
    """
    Constants to use for django ORMs `__weekday` lookup to avoid usage of integers directly.
    Unfortunately python's calendar weekdays are not equivalent to the database ones.
    """

    ORM_SUNDAY = 1
    ORM_MONDAY = 2
    ORM_TUESDAY = 3
    ORM_WEDNESDAY = 4
    ORM_THURSDAY = 5
    ORM_FRIDAY = 6
    ORM_SATURDAY = 7


def tz_today(str_format=None):
    """
    Returns either a timezone-aware today object or string. Depending on if the `str_format` param is set.
    :param str_format: If set, formats the date object to a string. Pass strftime-compatible value
    :return:
    """
    if settings.USE_TZ:
        date = timezone.now().date()
    else:
        date = datetime.datetime.now().date()

    if str_format:
        return date.strftime(str_format)
    return date


def add_months(
    source_date: Union[datetime.date, datetime.datetime], months: Union[int, float]
) -> Union[datetime.date, datetime.datetime]:
    return source_date + relativedelta(months=months)


def add_days(
    source_date: Union[datetime.date, datetime.datetime], days: int
) -> Union[datetime.date, datetime.datetime]:
    return source_date + datetime.timedelta(days=days)


def add_minutes(source_datetime: datetime.datetime, minutes: int) -> Union[datetime.date, datetime.datetime]:
    return source_datetime + relativedelta(minutes=minutes)


def get_next_month() -> datetime.date:
    return add_months(tz_today(), 1)


def first_day_of_month(source_date: datetime.date) -> datetime.date:
    return datetime.date(source_date.year, source_date.month, 1)


def get_formatted_date_str(source_date: Union[datetime.date, datetime.datetime]) -> str:
    return source_date.strftime('%d.%m.%Y')


def get_time_from_seconds(seconds: int) -> str:
    if seconds < 0:
        raise ValueError(_('Seconds must be positive.'))
    hours = seconds // 3600
    minutes = (seconds - (hours * 3600)) // 60
    seconds = seconds - ((hours * 3600) + (minutes * 60))
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


def datetime_format(target_datetime: datetime.datetime, dt_format: str) -> str:
    """
    Uses strftime, but considers timezone (only for datetime objects)
    """
    try:
        dt_format = target_datetime.astimezone(tz=pytz.timezone(settings.TIME_ZONE)).strftime(dt_format)
    except UnknownTimeZoneError:
        dt_format = target_datetime.strftime(dt_format)
    return dt_format


def get_start_and_end_date_from_calendar_week(year: int, calendar_week: int) -> (datetime.date, datetime.date):
    """
    Returns the first and last day of a given calendar week
    """
    monday = datetime.datetime.strptime(f'{year}-{calendar_week}-1', "%Y-%W-%w").astimezone().date()
    return monday, monday + datetime.timedelta(days=6.9)


def get_next_calendar_week(compare_date: datetime.date) -> int:
    """
    Returns the next calendar week as an integer
    """
    day_in_one_week = compare_date + datetime.timedelta(days=(7 - compare_date.weekday()))
    return day_in_one_week.isocalendar()[1]


def next_weekday(given_date: datetime.date, weekday: int) -> datetime.date:
    """
    Returns the next date of the given weekday
    For example: next_weekday(d, calendar.MONDAY) would return the next monday starting at date "given_date"
    """
    days_ahead = weekday - given_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return given_date + datetime.timedelta(days_ahead)


def date_month_delta(start_date: datetime.date, end_date: datetime.date) -> float:
    """
    Calculates the number of months lying between two dates.
    So from April 15th to May 1st it's 0.5 months.
    Attention: `end_date` will be excluded in the result (outer border)
    """
    # If `start_date` is greater, this logic doesn't make any sense
    if start_date > end_date:
        raise NotImplementedError('Start date > end date')

    # Calculate date difference between dates
    date_diff = (end_date - start_date).days

    # Iteration variable
    delta = 0
    iter_date = start_date
    # Loop until all days are processed
    while date_diff > 0:
        # Get days of month we are currently looking at
        iter_month, iter_month_days = monthrange(iter_date.year, iter_date.month)
        # Calculate how many days are left to end of this month
        days_to_month_end = min((iter_month_days - (iter_date.day - 1)), date_diff)
        # Add percentage of the month these days cover to return variable
        delta += days_to_month_end / iter_month_days
        # Reduce leftover days by the amount we already processed
        date_diff -= days_to_month_end

        # Set iteration date to first of next month
        iter_date += relativedelta(months=1, day=1)

    # Return data
    return delta


def get_first_and_last_of_month(date_object: datetime.date = None) -> Tuple[datetime.date, datetime.date]:
    """
    Returns first and last day of a month as date objects.
    Will either return first/last of current month (if no datetime_object is passed), or will determine first/last of
    the month of the passed datetime.date object
    """
    first_of_month = timezone.now().replace(day=1).date() if not date_object else date_object.replace(day=1)

    # Add one month to first_of_month
    first_of_next_month = first_of_month + relativedelta(months=1)

    # Subtract one day, to get the last of month
    last_of_month = first_of_next_month - datetime.timedelta(days=1)

    return first_of_month, last_of_month
