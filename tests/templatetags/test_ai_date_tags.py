from datetime import timedelta

from django.test import TestCase

from ambient_toolbox.templatetags.ai_date_tags import format_to_minutes


class AiDateTagTest(TestCase):
    def test_format_to_minutes_zero_seconds(self):
        """Test format_to_minutes with zero seconds"""
        td = timedelta(seconds=0)
        self.assertEqual(format_to_minutes(td), 0)

    def test_format_to_minutes_less_than_minute(self):
        """Test format_to_minutes with less than a minute"""
        td = timedelta(seconds=45)
        self.assertEqual(format_to_minutes(td), 0)

    def test_format_to_minutes_exactly_one_minute(self):
        """Test format_to_minutes with exactly one minute"""
        td = timedelta(seconds=60)
        self.assertEqual(format_to_minutes(td), 1)

    def test_format_to_minutes_multiple_minutes(self):
        """Test format_to_minutes with multiple minutes"""
        td = timedelta(seconds=300)  # 5 minutes
        self.assertEqual(format_to_minutes(td), 5)

    def test_format_to_minutes_with_remainder(self):
        """Test format_to_minutes with remainder seconds"""
        td = timedelta(seconds=125)  # 2 minutes and 5 seconds
        self.assertEqual(format_to_minutes(td), 2)

    def test_format_to_minutes_large_value(self):
        """Test format_to_minutes with large number of seconds"""
        td = timedelta(seconds=3661)  # 1 hour, 1 minute, 1 second
        self.assertEqual(format_to_minutes(td), 61)

    def test_format_to_minutes_with_days(self):
        """Test format_to_minutes with timedelta that includes days"""
        # Note: timedelta.seconds only returns the seconds component (0-86399),
        # not the total seconds including days
        td = timedelta(days=1, seconds=120)  # 1 day + 2 minutes
        self.assertEqual(format_to_minutes(td), 2)
