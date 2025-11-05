import calendar
import datetime

import pytest
from django.test.utils import override_settings
from freezegun import freeze_time

from ambient_toolbox.utils import get_previous_quarter_starting_date_for_date
from ambient_toolbox.utils.date import (
    DateHelper,
    MonthHelper,
    add_days,
    add_minutes,
    add_months,
    check_date_is_weekend,
    date_month_delta,
    datetime_format,
    first_day_of_month,
    get_current_year,
    get_first_and_last_of_month,
    get_formatted_date_str,
    get_next_calendar_week,
    get_next_month,
    get_start_and_end_date_from_calendar_week,
    get_time_from_seconds,
    next_weekday,
    tz_today,
)

# ==============================================================================
# MonthHelper
# ==============================================================================


def test_month_helper_january():
    assert MonthHelper.JANUARY == 1


def test_month_helper_february():
    assert MonthHelper.FEBRUARY == 2  # noqa: PLR2004


def test_month_helper_march():
    assert MonthHelper.MARCH == 3  # noqa: PLR2004


def test_month_helper_april():
    assert MonthHelper.APRIL == 4  # noqa: PLR2004


def test_month_helper_may():
    assert MonthHelper.MAY == 5  # noqa: PLR2004


def test_month_helper_june():
    assert MonthHelper.JUNE == 6  # noqa: PLR2004


def test_month_helper_july():
    assert MonthHelper.JULY == 7  # noqa: PLR2004


def test_month_helper_august():
    assert MonthHelper.AUGUST == 8  # noqa: PLR2004


def test_month_helper_september():
    assert MonthHelper.SEPTEMBER == 9  # noqa: PLR2004


def test_month_helper_october():
    assert MonthHelper.OCTOBER == 10  # noqa: PLR2004


def test_month_helper_november():
    assert MonthHelper.NOVEMBER == 11  # noqa: PLR2004


def test_month_helper_december():
    assert MonthHelper.DECEMBER == 12  # noqa: PLR2004


# ==============================================================================
# DateHelper
# ==============================================================================


def test_date_helper_orm_sunday():
    assert DateHelper.ORM_SUNDAY == 1


def test_date_helper_orm_monday():
    assert DateHelper.ORM_MONDAY == 2  # noqa: PLR2004


def test_date_helper_orm_tuesday():
    assert DateHelper.ORM_TUESDAY == 3  # noqa: PLR2004


def test_date_helper_orm_wednesday():
    assert DateHelper.ORM_WEDNESDAY == 4  # noqa: PLR2004


def test_date_helper_orm_thursday():
    assert DateHelper.ORM_THURSDAY == 5  # noqa: PLR2004


def test_date_helper_orm_friday():
    assert DateHelper.ORM_FRIDAY == 6  # noqa: PLR2004


def test_date_helper_orm_saturday():
    assert DateHelper.ORM_SATURDAY == 7  # noqa: PLR2004


# ==============================================================================
# tz_today
# ==============================================================================


@override_settings(USE_TZ=True)
def test_tz_today_with_tz_enabled():
    """Test tz_today returns correct date when USE_TZ is True."""
    frozen_date = datetime.datetime(year=2019, month=9, day=19, hour=10)
    with freeze_time(frozen_date):
        assert tz_today() == frozen_date.date()


@override_settings(USE_TZ=False)
def test_tz_today_with_tz_disabled():
    """Test tz_today returns correct date when USE_TZ is False."""
    frozen_date = datetime.datetime(year=2019, month=9, day=19, hour=10)
    with freeze_time(frozen_date):
        assert tz_today() == frozen_date.date()


@override_settings(USE_TZ=True)
def test_tz_today_with_string_format():
    """Test tz_today returns formatted string when str_format is provided."""
    frozen_date = datetime.datetime(year=2019, month=9, day=19, hour=10)
    with freeze_time(frozen_date):
        assert tz_today("%d.%m.%Y") == "19.09.2019"


# ==============================================================================
# add_months
# ==============================================================================


def test_add_months_with_date_one_month():
    """Test adding one month to a date object."""
    source_date = datetime.date(year=2020, month=6, day=26)
    assert add_months(source_date, 1) == datetime.date(year=2020, month=7, day=26)


def test_add_months_with_date_many_months():
    """Test adding many months to a date object."""
    source_date = datetime.date(year=2020, month=6, day=26)
    assert add_months(source_date, 10) == datetime.date(year=2021, month=4, day=26)


def test_add_months_with_date_negative_months():
    """Test subtracting months from a date object."""
    source_date = datetime.date(year=2020, month=6, day=26)
    assert add_months(source_date, -2) == datetime.date(year=2020, month=4, day=26)


def test_add_months_with_datetime_one_month():
    """Test adding one month to a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=10, minute=30)
    assert add_months(source_datetime, 1) == datetime.datetime(year=2020, month=7, day=26, hour=10, minute=30)


def test_add_months_with_datetime_many_months():
    """Test adding many months to a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=10, minute=30)
    assert add_months(source_datetime, 10) == datetime.datetime(year=2021, month=4, day=26, hour=10, minute=30)


def test_add_months_with_datetime_negative_months():
    """Test subtracting months from a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=10, minute=30)
    assert add_months(source_datetime, -2) == datetime.datetime(year=2020, month=4, day=26, hour=10, minute=30)


# ==============================================================================
# add_days
# ==============================================================================


def test_add_days_with_date_one_day():
    """Test adding one day to a date object."""
    source_date = datetime.date(year=2020, month=6, day=26)
    assert add_days(source_date, 1) == datetime.date(year=2020, month=6, day=27)


def test_add_days_with_date_many_days():
    """Test adding many days to a date object."""
    source_date = datetime.date(year=2020, month=6, day=26)
    assert add_days(source_date, 10) == datetime.date(year=2020, month=7, day=6)


def test_add_days_with_date_negative_days():
    """Test subtracting days from a date object."""
    source_date = datetime.date(year=2020, month=6, day=26)
    assert add_days(source_date, -2) == datetime.date(year=2020, month=6, day=24)


def test_add_days_with_datetime_one_day():
    """Test adding one day to a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=10, minute=30)
    assert add_days(source_datetime, 1) == datetime.datetime(year=2020, month=6, day=27, hour=10, minute=30)


def test_add_days_with_datetime_many_days():
    """Test adding many days to a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=10, minute=30)
    assert add_days(source_datetime, 10) == datetime.datetime(year=2020, month=7, day=6, hour=10, minute=30)


def test_add_days_with_datetime_negative_days():
    """Test subtracting days from a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=10, minute=30)
    assert add_days(source_datetime, -2) == datetime.datetime(year=2020, month=6, day=24, hour=10, minute=30)


# ==============================================================================
# add_minutes
# ==============================================================================


def test_add_minutes_one_minute():
    """Test adding one minute to a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=8, minute=0)
    assert add_minutes(source_datetime, 1) == datetime.datetime(year=2020, month=6, day=26, hour=8, minute=1)


def test_add_minutes_many_minutes():
    """Test adding many minutes to a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=8, minute=0)
    assert add_minutes(source_datetime, 10) == datetime.datetime(year=2020, month=6, day=26, hour=8, minute=10)


def test_add_minutes_negative_minutes():
    """Test subtracting minutes from a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=8, minute=0)
    assert add_minutes(source_datetime, -2) == datetime.datetime(year=2020, month=6, day=26, hour=7, minute=58)


# ==============================================================================
# get_next_month
# ==============================================================================


@freeze_time("2020-06-26")
def test_get_next_month():
    """Test getting the next month from today."""
    assert get_next_month() == datetime.date(year=2020, month=7, day=26)


# ==============================================================================
# first_day_of_month
# ==============================================================================


def test_first_day_of_month():
    """Test getting the first day of a month."""
    source_date = datetime.date(year=2020, month=6, day=26)
    assert first_day_of_month(source_date) == datetime.date(year=2020, month=6, day=1)


# ==============================================================================
# get_formatted_date_str
# ==============================================================================


def test_get_formatted_date_str_with_date():
    """Test formatting a date object."""
    source_date = datetime.date(year=2020, month=6, day=26)
    assert get_formatted_date_str(source_date) == "26.06.2020"


def test_get_formatted_date_str_with_datetime():
    """Test formatting a datetime object."""
    source_datetime = datetime.datetime(year=2020, month=6, day=26, hour=10, minute=30)
    assert get_formatted_date_str(source_datetime) == "26.06.2020"


# ==============================================================================
# get_time_from_seconds
# ==============================================================================


def test_get_time_from_seconds_one_hour():
    """Test converting 3600 seconds to time string."""
    assert get_time_from_seconds(3600) == "01:00:00"


def test_get_time_from_seconds_one_minute():
    """Test converting 60 seconds to time string."""
    assert get_time_from_seconds(60) == "00:01:00"


def test_get_time_from_seconds_big_hours():
    """Test converting large number of seconds with double-digit hours."""
    assert get_time_from_seconds(3600 * 99) == "99:00:00"


def test_get_time_from_seconds_huge_hours():
    """Test converting very large number of seconds with four-digit hours."""
    assert get_time_from_seconds(3600 * 1000) == "1000:00:00"


def test_get_time_from_seconds_negative_seconds():
    """Test that negative seconds raises ValueError."""
    with pytest.raises(ValueError):
        get_time_from_seconds(-1)


# ==============================================================================
# datetime_format
# ==============================================================================


@override_settings(TIME_ZONE="UTC")
def test_datetime_format_with_utc_timezone():
    """Test datetime formatting with UTC timezone."""
    source_date = datetime.datetime(year=2020, month=6, day=26, hour=8, tzinfo=datetime.timezone.utc)
    assert datetime_format(source_date, "%d.%m.%Y %H:%M") == "26.06.2020 08:00"


@override_settings(TIME_ZONE="Europe/Cologne")
def test_datetime_format_with_cologne_timezone():
    """Test datetime formatting with Europe/Cologne timezone (same as UTC in summer)."""
    source_date = datetime.datetime(year=2020, month=6, day=26, hour=8, tzinfo=datetime.timezone.utc)
    assert datetime_format(source_date, "%d.%m.%Y %H:%M") == "26.06.2020 08:00"


@override_settings(TIME_ZONE="Europe/Berlin")
def test_datetime_format_with_berlin_timezone():
    """Test datetime formatting with Europe/Berlin timezone (UTC+2 in summer)."""
    source_date = datetime.datetime(year=2020, month=6, day=26, hour=8, tzinfo=datetime.timezone.utc)
    assert datetime_format(source_date, "%d.%m.%Y %H:%M") == "26.06.2020 10:00"


@override_settings(TIME_ZONE="Invalid/Timezone")
def test_datetime_format_with_invalid_timezone():
    """Test that datetime_format handles ZoneInfoNotFoundError gracefully."""
    source_date = datetime.datetime(year=2020, month=6, day=26, hour=8, tzinfo=datetime.timezone.utc)
    assert datetime_format(source_date, "%d.%m.%Y %H:%M") == "26.06.2020 08:00"


# ==============================================================================
# get_start_and_end_date_from_calendar_week
# ==============================================================================


def test_get_start_and_end_date_from_calendar_week_spanning_year():
    """Test calendar week spanning two years (2016 week 52)."""
    monday, sunday = get_start_and_end_date_from_calendar_week(2016, 52)
    assert monday == datetime.date(year=2016, month=12, day=26)
    assert sunday == datetime.date(year=2017, month=1, day=1)


def test_get_start_and_end_date_from_calendar_week_first_week_2018():
    """Test first calendar week of 2018."""
    monday, sunday = get_start_and_end_date_from_calendar_week(2018, 1)
    assert monday == datetime.date(year=2018, month=1, day=1)
    assert sunday == datetime.date(year=2018, month=1, day=7)


def test_get_start_and_end_date_from_calendar_week_first_week_2020():
    """Test first calendar week of 2020 (starts in previous year)."""
    monday, sunday = get_start_and_end_date_from_calendar_week(2020, 1)
    assert monday == datetime.date(year=2019, month=12, day=30)
    assert sunday == datetime.date(year=2020, month=1, day=5)


def test_get_start_and_end_date_from_calendar_week_mid_year():
    """Test a mid-year calendar week."""
    monday, sunday = get_start_and_end_date_from_calendar_week(2017, 30)
    assert monday == datetime.date(year=2017, month=7, day=24)
    assert sunday == datetime.date(year=2017, month=7, day=30)


def test_get_start_and_end_date_from_calendar_week_2025():
    """Test calendar week 3 of 2025."""
    monday, sunday = get_start_and_end_date_from_calendar_week(2025, 3)
    assert monday == datetime.date(year=2025, month=1, day=13)
    assert sunday == datetime.date(year=2025, month=1, day=19)


def test_get_start_and_end_date_from_calendar_week_2026():
    """Test calendar week 3 of 2026."""
    monday, sunday = get_start_and_end_date_from_calendar_week(2026, 3)
    assert monday == datetime.date(year=2026, month=1, day=12)
    assert sunday == datetime.date(year=2026, month=1, day=18)


def test_get_start_and_end_date_from_calendar_week_year_starting_friday():
    """Test calendar week calculation when year starts on Friday (2016)."""
    monday, sunday = get_start_and_end_date_from_calendar_week(2016, 1)
    assert monday == datetime.date(year=2016, month=1, day=4)
    assert sunday == datetime.date(year=2016, month=1, day=10)


def test_get_start_and_end_date_from_calendar_week_year_starting_saturday():
    """Test calendar week calculation when year starts on Saturday (2022)."""
    monday, sunday = get_start_and_end_date_from_calendar_week(2022, 1)
    assert monday == datetime.date(year=2022, month=1, day=3)
    assert sunday == datetime.date(year=2022, month=1, day=9)


def test_get_start_and_end_date_from_calendar_week_year_starting_sunday():
    """Test calendar week calculation when year starts on Sunday (2023)."""
    monday, sunday = get_start_and_end_date_from_calendar_week(2023, 1)
    assert monday == datetime.date(year=2023, month=1, day=2)
    assert sunday == datetime.date(year=2023, month=1, day=8)


# ==============================================================================
# get_next_calendar_week
# ==============================================================================


def test_get_next_calendar_week_mid_year():
    """Test getting next calendar week in the middle of the year."""
    assert get_next_calendar_week(datetime.date(year=2020, month=9, day=19)) == 39  # noqa: PLR2004


def test_get_next_calendar_week_beginning_of_year():
    """Test getting next calendar week at the beginning of the year."""
    assert get_next_calendar_week(datetime.date(year=2020, month=1, day=1)) == 2  # noqa: PLR2004


def test_get_next_calendar_week_end_of_year():
    """Test getting next calendar week at the end of the year (wraps to week 1)."""
    assert get_next_calendar_week(datetime.date(year=2020, month=12, day=31)) == 1


# ==============================================================================
# next_weekday
# ==============================================================================


def test_next_weekday_forward_multiple_days():
    """Test getting next Friday from a Saturday."""
    assert next_weekday(datetime.date(year=2020, month=9, day=19), calendar.FRIDAY) == datetime.date(
        year=2020, month=9, day=25
    )


def test_next_weekday_same_day_next_week():
    """Test getting next Saturday from a Saturday (should be next week)."""
    assert next_weekday(datetime.date(year=2020, month=9, day=19), calendar.SATURDAY) == datetime.date(
        year=2020, month=9, day=26
    )


def test_next_weekday_forward_in_same_week():
    """Test when the desired weekday is ahead in the current week."""
    # Monday (2020-09-21) to Friday (same week)
    assert next_weekday(datetime.date(year=2020, month=9, day=21), calendar.FRIDAY) == datetime.date(
        year=2020, month=9, day=25
    )


# ==============================================================================
# date_month_delta
# ==============================================================================


def test_date_month_delta_one_month():
    """Test date delta of exactly one month."""
    start_date = datetime.date(year=2017, month=2, day=1)
    end_date = datetime.date(year=2017, month=3, day=1)
    assert date_month_delta(start_date, end_date) == 1


def test_date_month_delta_half_month():
    """Test date delta of approximately half a month."""
    start_date = datetime.date(year=2017, month=4, day=15)
    end_date = datetime.date(year=2017, month=5, day=1)
    assert date_month_delta(start_date, end_date) == pytest.approx(0.5, abs=0.1)


def test_date_month_delta_one_and_half_months():
    """Test date delta of approximately 1.5 months."""
    start_date = datetime.date(year=2017, month=4, day=15)
    end_date = datetime.date(year=2017, month=6, day=1)
    assert date_month_delta(start_date, end_date) == pytest.approx(1.5, abs=0.1)


def test_date_month_delta_full_year():
    """Test date delta of exactly one year (12 months)."""
    start_date = datetime.date(year=2017, month=1, day=1)
    end_date = datetime.date(year=2018, month=1, day=1)
    assert date_month_delta(start_date, end_date) == 12  # noqa: PLR2004


def test_date_month_delta_two_and_half_years():
    """Test date delta of 30 months (2.5 years)."""
    start_date = datetime.date(year=2017, month=1, day=1)
    end_date = datetime.date(year=2019, month=7, day=1)
    assert date_month_delta(start_date, end_date) == 30  # noqa: PLR2004


def test_date_month_delta_no_difference():
    """Test date delta when start and end dates are the same."""
    start_date = datetime.date(year=2017, month=4, day=15)
    end_date = datetime.date(year=2017, month=4, day=15)
    assert date_month_delta(start_date, end_date) == 0


def test_date_month_delta_one_day():
    """Test date delta of exactly one day."""
    start_date = datetime.date(year=2017, month=4, day=15)
    end_date = datetime.date(year=2017, month=4, day=16)
    assert date_month_delta(start_date, end_date) == 1 / 30


def test_date_month_delta_start_greater_than_end():
    """Test that start date greater than end date raises NotImplementedError."""
    start_date = datetime.date(year=2017, month=4, day=15)
    end_date = datetime.date(year=2017, month=4, day=14)
    with pytest.raises(NotImplementedError):
        date_month_delta(start_date, end_date)


# ==============================================================================
# get_first_and_last_of_month
# ==============================================================================


@freeze_time("2022-12-14")
def test_get_first_and_last_of_month_december():
    """Test getting first and last day of December."""
    first_of_month, last_of_month = get_first_and_last_of_month()
    assert first_of_month == datetime.date(day=1, month=12, year=2022)
    assert last_of_month == datetime.date(day=31, month=12, year=2022)


@freeze_time("2020-02-14")
def test_get_first_and_last_of_month_february_leap_year():
    """Test getting first and last day of February in a leap year."""
    first_of_month, last_of_month = get_first_and_last_of_month()
    assert first_of_month == datetime.date(day=1, month=2, year=2020)
    assert last_of_month == datetime.date(day=29, month=2, year=2020)


@freeze_time("2022-02-14")
def test_get_first_and_last_of_month_february_non_leap_year():
    """Test getting first and last day of February in a non-leap year."""
    first_of_month, last_of_month = get_first_and_last_of_month()
    assert first_of_month == datetime.date(day=1, month=2, year=2022)
    assert last_of_month == datetime.date(day=28, month=2, year=2022)


@freeze_time("2022-04-04")
def test_get_first_and_last_of_month_april():
    """Test getting first and last day of April."""
    first_of_month, last_of_month = get_first_and_last_of_month()
    assert first_of_month == datetime.date(day=1, month=4, year=2022)
    assert last_of_month == datetime.date(day=30, month=4, year=2022)


def test_get_first_and_last_of_month_with_date_object_december():
    """Test getting first and last day with explicit date object for December."""
    date_object = datetime.date(day=14, month=12, year=2022)
    first_of_month, last_of_month = get_first_and_last_of_month(date_object=date_object)
    assert first_of_month == datetime.date(day=1, month=12, year=2022)
    assert last_of_month == datetime.date(day=31, month=12, year=2022)


def test_get_first_and_last_of_month_with_date_object_february_leap_year():
    """Test getting first and last day with explicit date object for February leap year."""
    date_object = datetime.date(day=14, month=2, year=2020)
    first_of_month, last_of_month = get_first_and_last_of_month(date_object=date_object)
    assert first_of_month == datetime.date(day=1, month=2, year=2020)
    assert last_of_month == datetime.date(day=29, month=2, year=2020)


def test_get_first_and_last_of_month_with_date_object_february_non_leap_year():
    """Test getting first and last day with explicit date object for February non-leap year."""
    date_object = datetime.date(day=14, month=2, year=2022)
    first_of_month, last_of_month = get_first_and_last_of_month(date_object=date_object)
    assert first_of_month == datetime.date(day=1, month=2, year=2022)
    assert last_of_month == datetime.date(day=28, month=2, year=2022)


def test_get_first_and_last_of_month_with_date_object_april():
    """Test getting first and last day with explicit date object for April."""
    date_object = datetime.date(day=4, month=4, year=2022)
    first_of_month, last_of_month = get_first_and_last_of_month(date_object=date_object)
    assert first_of_month == datetime.date(day=1, month=4, year=2022)
    assert last_of_month == datetime.date(day=30, month=4, year=2022)


# ==============================================================================
# get_current_year
# ==============================================================================


@freeze_time("2017-06-26")
def test_get_current_year_mid_year():
    """Test getting current year in the middle of the year."""
    assert get_current_year() == 2017  # noqa: PLR2004


@freeze_time("2017-12-31 23:59")
def test_get_current_year_end_of_year():
    """Test getting current year at the end of the year."""
    assert get_current_year() == 2017  # noqa: PLR2004


@freeze_time("2017-01-01 00:00")
def test_get_current_year_beginning_of_year():
    """Test getting current year at the beginning of the year."""
    assert get_current_year() == 2017  # noqa: PLR2004


# ==============================================================================
# check_date_is_weekend
# ==============================================================================


def test_check_date_is_weekend_weekday():
    """Test that a weekday (Thursday) is not a weekend."""
    compare_date = datetime.date(year=2024, month=9, day=19)
    assert check_date_is_weekend(compare_date) is False


def test_check_date_is_weekend_saturday():
    """Test that Saturday is a weekend day."""
    compare_date = datetime.date(year=2024, month=9, day=21)
    assert check_date_is_weekend(compare_date) is True


def test_check_date_is_weekend_custom_friday_saturday():
    """Test weekend checking with custom weekend days (Friday and Saturday)."""
    # Thursday - not weekend
    thursday = datetime.date(year=2024, month=9, day=19)
    assert check_date_is_weekend(thursday, weekend_days=(calendar.FRIDAY, calendar.SATURDAY)) is False

    # Friday - weekend in custom setup
    friday = datetime.date(year=2024, month=9, day=20)
    assert check_date_is_weekend(friday, weekend_days=(calendar.FRIDAY, calendar.SATURDAY)) is True

    # Saturday - weekend in custom setup
    saturday = datetime.date(year=2024, month=9, day=21)
    assert check_date_is_weekend(saturday, weekend_days=(calendar.FRIDAY, calendar.SATURDAY)) is True

    # Sunday - not weekend in custom setup
    sunday = datetime.date(year=2024, month=9, day=22)
    assert check_date_is_weekend(sunday, weekend_days=(calendar.FRIDAY, calendar.SATURDAY)) is False


def test_check_date_is_weekend_single_day():
    """Test weekend checking with only one weekend day."""
    friday = datetime.date(year=2024, month=9, day=20)
    saturday = datetime.date(year=2024, month=9, day=21)

    # Only Friday is weekend
    assert check_date_is_weekend(friday, weekend_days=(calendar.FRIDAY,)) is True
    assert check_date_is_weekend(saturday, weekend_days=(calendar.FRIDAY,)) is False


# ==============================================================================
# get_previous_quarter_starting_date_for_date
# ==============================================================================


def test_get_previous_quarter_starting_date_q1_to_q4():
    """Test getting previous quarter from Q1 (returns Q4 of previous year)."""
    date = datetime.date(year=2025, month=1, day=1)
    assert get_previous_quarter_starting_date_for_date(date=date) == datetime.date(2024, 10, 1)


def test_get_previous_quarter_starting_date_q2_to_q1():
    """Test getting previous quarter from Q2 (returns Q1)."""
    date = datetime.date(year=2025, month=4, day=1)
    assert get_previous_quarter_starting_date_for_date(date=date) == datetime.date(2025, 1, 1)


def test_get_previous_quarter_starting_date_q3_to_q2():
    """Test getting previous quarter from Q3 (returns Q2)."""
    date = datetime.date(year=2025, month=7, day=1)
    assert get_previous_quarter_starting_date_for_date(date=date) == datetime.date(2025, 4, 1)


def test_get_previous_quarter_starting_date_q4_to_q3():
    """Test getting previous quarter from Q4 (returns Q3)."""
    date = datetime.date(year=2025, month=10, day=1)
    assert get_previous_quarter_starting_date_for_date(date=date) == datetime.date(2025, 7, 1)
