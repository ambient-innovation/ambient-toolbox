from django.test import TestCase

from ambient_toolbox.templatetags.ai_number_tags import currency, divide, multiply, subtract, to_int


class AiNumberTagTest(TestCase):
    def test_multiply_regular(self):
        self.assertEqual(multiply(3, 3), 9)

    def test_multiply_string(self):
        self.assertEqual(multiply("3", 3), 9)

    def test_multiply_german_float(self):
        self.assertEqual(multiply("3,19", 3), 9.57)

    def test_multiply_no_value(self):
        self.assertIsNone(multiply(None, 3))

    def test_subtract_regular(self):
        self.assertEqual(subtract(4, 1), 3)

    def test_divide_regular(self):
        self.assertEqual(divide(8, 2), 4)

    def test_divide_no_value(self):
        self.assertEqual(divide(None, 2), None)

    def test_to_int_case_number(self):
        self.assertEqual(to_int("42"), 42)

    def test_to_int_case_text(self):
        self.assertEqual(to_int("Aubrey"), 0)

    def test_currency_regular(self):
        self.assertEqual(currency(12.4), "12,40€")

    def test_currency_no_value(self):
        self.assertEqual(currency(None), "-")
