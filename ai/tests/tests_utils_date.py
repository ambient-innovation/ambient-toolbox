import datetime
from unittest import TestCase

from ai.utils.date import date_month_delta, get_start_and_end_date_from_calendar_week


class DateUtilTest(TestCase):
    TEST_CURRENT_YEAR = 2017

    def setUp(self):
        # BaseTest setup
        super(DateUtilTest, self).setUp()

    def test_get_start_and_end_date_from_calendar_week(self):
        monday, sunday = get_start_and_end_date_from_calendar_week(2016, 52)
        self.assertEquals(monday, datetime.date(year=2016, month=12, day=26))

        monday, sunday = get_start_and_end_date_from_calendar_week(2018, 1)
        self.assertEquals(monday, datetime.date(year=2018, month=1, day=1))

        monday, sunday = get_start_and_end_date_from_calendar_week(2017, 30)
        self.assertEquals(monday, datetime.date(year=2017, month=7, day=24))

    def test_date_month_delta(self):
        start_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=2, day=1)
        end_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=3, day=1)
        self.assertEqual(date_month_delta(start_date, end_date), 1)

    def test_date_month_delta_half_month(self):
        start_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=4, day=15)
        end_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=5, day=1)
        self.assertAlmostEqual(date_month_delta(start_date, end_date), 0.5, 1)

    def test_date_month_delta_one_and_a_half_month(self):
        start_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=4, day=15)
        end_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=6, day=1)
        self.assertAlmostEqual(date_month_delta(start_date, end_date), 1.5, 1)

    def test_date_month_delta_full_year(self):
        start_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=1, day=1)
        end_date = datetime.date(year=self.TEST_CURRENT_YEAR + 1, month=1, day=1)
        self.assertEqual(date_month_delta(start_date, end_date), 12)

    def test_date_month_delta_two_years(self):
        start_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=1, day=1)
        end_date = datetime.date(year=self.TEST_CURRENT_YEAR + 2, month=7, day=1)
        self.assertEqual(date_month_delta(start_date, end_date), 30)

    def test_date_month_delta_no_difference(self):
        start_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=4, day=15)
        end_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=4, day=15)
        self.assertEqual(date_month_delta(start_date, end_date), 0)

    def test_date_month_delta_one_day(self):
        start_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=4, day=15)
        end_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=4, day=16)
        self.assertEqual(date_month_delta(start_date, end_date), 1 / 30)

    def test_date_month_delta_start_greater_then_end_date(self):
        start_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=4, day=15)
        end_date = datetime.date(year=self.TEST_CURRENT_YEAR, month=4, day=14)
        self.assertRaises(NotImplementedError, date_month_delta, start_date, end_date)