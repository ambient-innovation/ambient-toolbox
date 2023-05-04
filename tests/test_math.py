from django.test import TestCase

from ambient_toolbox.utils.math import round_to_decimal, round_up_decimal


class MathTest(TestCase):
    def test_round_to_decimal_no_precision(self):
        self.assertEqual(round_to_decimal(5.2, 1), 5)

    def test_round_to_decimal_two_precisions(self):
        self.assertEqual(round_to_decimal(5.62, 0.05), 5.60)

    def test_round_to_decimal_down_lower(self):
        self.assertEqual(round_to_decimal(5.2), 5.0)

    def test_round_to_decimal_up_lower(self):
        self.assertEqual(round_to_decimal(5.4), 5.5)

    def test_round_to_decimal_down_upper(self):
        self.assertEqual(round_to_decimal(5.6), 5.5)

    def test_round_to_decimal_no_round(self):
        self.assertEqual(round_to_decimal(5.0), 5.0)

    def test_round_to_decimal_up_upper(self):
        self.assertEqual(round_to_decimal(5.8), 6.0)

    def test_round_up_decimal_no_precision(self):
        self.assertEqual(round_up_decimal(5.2, 1), 6)

    def test_round_up_decimal_two_precisions(self):
        self.assertEqual(round_up_decimal(5.62, 0.05), 5.65)

    def test_round_up_decimal_down_lower(self):
        self.assertEqual(round_up_decimal(5.2), 5.5)

    def test_round_up_decimal_up_lower(self):
        self.assertEqual(round_up_decimal(5.4), 5.5)

    def test_round_up_decimal_down_upper(self):
        self.assertEqual(round_up_decimal(5.6), 6.0)

    def test_round_up_decimal_no_round(self):
        self.assertEqual(round_up_decimal(5.0), 5.0)

    def test_round_up_decimal_up_upper(self):
        self.assertEqual(round_up_decimal(5.8), 6.0)
