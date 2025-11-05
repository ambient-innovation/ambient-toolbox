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

    def test_multiply_empty_string(self):
        """Test multiply with empty string returns None"""
        self.assertIsNone(multiply("", 3))

    def test_multiply_zero(self):
        """Test multiply with zero returns None (falsy value)"""
        self.assertIsNone(multiply(0, 3))

    def test_multiply_false(self):
        """Test multiply with False returns None"""
        self.assertIsNone(multiply(False, 3))

    def test_multiply_custom_object_with_empty_string_representation(self):
        """Test multiply with object that is truthy but stringifies to empty"""

        class WeirdObject:
            def __bool__(self):
                return True

            def __str__(self):
                return ""

        result = multiply(WeirdObject(), 3)
        # Should return None because string representation is empty
        self.assertIsNone(result)

    def test_subtract_regular(self):
        self.assertEqual(subtract(4, 1), 3)

    def test_subtract_none_value(self):
        """Test subtract with None value (uses 0)"""
        self.assertEqual(subtract(None, 5), -5)

    def test_subtract_none_arg(self):
        """Test subtract with None arg (uses 0)"""
        self.assertEqual(subtract(10, None), 10)

    def test_subtract_both_none(self):
        """Test subtract with both None (0 - 0)"""
        self.assertEqual(subtract(None, None), 0)

    def test_divide_regular(self):
        self.assertEqual(divide(8, 2), 4)

    def test_divide_no_value(self):
        self.assertEqual(divide(None, 2), None)

    def test_divide_zero_value(self):
        """Test divide with 0 value returns None"""
        self.assertEqual(divide(0, 2), None)

    def test_divide_false_value(self):
        """Test divide with False returns None"""
        self.assertEqual(divide(False, 2), None)

    def test_divide_float(self):
        """Test divide with float values"""
        self.assertEqual(divide(10.0, 2.5), 4.0)

    def test_to_int_case_number(self):
        self.assertEqual(to_int("42"), 42)

    def test_to_int_case_text(self):
        self.assertEqual(to_int("Aubrey"), 0)

    def test_to_int_negative_number(self):
        """Test to_int with negative number"""
        self.assertEqual(to_int("-42"), -42)

    def test_to_int_zero(self):
        """Test to_int with zero"""
        self.assertEqual(to_int("0"), 0)

    def test_to_int_float_string(self):
        """Test to_int with float string (should fail and return 0)"""
        self.assertEqual(to_int("3.14"), 0)

    def test_currency_regular(self):
        self.assertEqual(currency(12.4), "12,40€")

    def test_currency_no_value(self):
        self.assertEqual(currency(None), "-")

    def test_currency_zero(self):
        """Test currency with zero returns dash"""
        self.assertEqual(currency(0), "-")

    def test_currency_false(self):
        """Test currency with False returns dash"""
        self.assertEqual(currency(False), "-")

    def test_currency_integer(self):
        """Test currency with integer value"""
        self.assertEqual(currency(10), "10,00€")

    def test_currency_rounding(self):
        """Test currency properly rounds to 2 decimal places"""
        self.assertEqual(currency(12.456), "12,46€")
        self.assertEqual(currency(12.454), "12,45€")
