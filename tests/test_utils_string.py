import datetime

import pytz
from django.test import TestCase

from ambient_toolbox.utils.string import (
    date_to_string,
    datetime_to_string,
    distinct,
    encode_to_xml,
    float_to_string,
    number_to_string,
    slugify_file_name,
    smart_truncate,
    string_or_none_to_string,
)


class UtilsStringTest(TestCase):
    def test_distinct_regular(self):
        not_distinct_list = ["Beer", "Wine", "Whiskey", "Beer"]
        distinct_list = distinct(not_distinct_list)

        self.assertEqual(len(distinct_list), 3)
        self.assertIn("Beer", distinct_list)
        self.assertIn("Whiskey", distinct_list)
        self.assertIn("Wine", distinct_list)

    def test_slugify_file_name_regular(self):
        filename = "hola and hello.txt"
        slug = slugify_file_name(filename)
        self.assertEqual(slug, "hola_and_hello.txt")

    def test_slugify_file_name_nothing_to_slugify(self):
        filename = "hola.txt"
        slug = slugify_file_name(filename)
        self.assertEqual(slug, filename)

    def test_slugify_file_name_max_length(self):
        filename = "a very long filename.txt"
        slug = slugify_file_name(filename, 6)
        self.assertEqual(slug, "a_very.txt")

    def test_smart_truncate_in_word(self):
        my_sentence = "I am a very interesting sentence."
        truncated_str = smart_truncate(my_sentence, 10)
        self.assertEqual(truncated_str, "I am a...")

    def test_smart_truncate_after_word(self):
        my_sentence = "I am a very interesting sentence."
        truncated_str = smart_truncate(my_sentence, 14)
        self.assertEqual(truncated_str, "I am a very...")

    def test_smart_truncate_changed_postfix(self):
        my_sentence = "I am a very interesting sentence."
        truncated_str = smart_truncate(my_sentence, 10, "[...]")
        self.assertEqual(truncated_str, "I am a[...]")

    def test_smart_truncate_not_cutting_on_too_short_strings(self):
        my_sentence = "I am a very interesting sentence."
        truncated_str = smart_truncate(my_sentence, 100, "---")
        self.assertEqual(truncated_str, my_sentence)

    def test_smart_truncate_no_text(self):
        truncated_str = smart_truncate(None, 100, "---")
        self.assertEqual(truncated_str, "")

    def test_float_to_string_regular(self):
        self.assertEqual(float_to_string(5.61), "5,61")

    def test_float_to_string_value_replacement_not_used(self):
        self.assertEqual(float_to_string(4.41, "-"), "4,41")

    def test_float_to_string_no_value_replacement_used(self):
        self.assertEqual(float_to_string(None, "Heureka"), "Heureka")

    def test_float_to_string_value_greater_thousand(self):
        self.assertEqual(float_to_string(1234.56), "1234,56")

    def test_date_to_string_regular(self):
        self.assertEqual(date_to_string(datetime.date(2020, 9, 19)), "19.09.2020")

    def test_date_to_string_other_format(self):
        self.assertEqual(date_to_string(datetime.date(2020, 9, 19), str_format="%Y-%m-%d"), "2020-09-19")

    def test_date_to_string_replacement_undefined(self):
        self.assertEqual(date_to_string(None), "-")

    def test_date_to_string_replacement_defined(self):
        self.assertEqual(date_to_string(None, "no date"), "no date")

    def test_datetime_to_string_regular(self):
        self.assertEqual(datetime_to_string(datetime.datetime(2020, 9, 19, 8, tzinfo=pytz.UTC)), "19.09.2020 08:00")

    def test_datetime_to_string_other_format(self):
        self.assertEqual(
            datetime_to_string(datetime.datetime(2020, 9, 19, 8, tzinfo=pytz.UTC), str_format="%Y-%m-%d"), "2020-09-19"
        )

    def test_datetime_to_string_replacement_undefined(self):
        self.assertEqual(datetime_to_string(None), "-")

    def test_datetime_to_string_replacement_defined(self):
        self.assertEqual(datetime_to_string(None, "no date"), "no date")

    def test_number_to_string_regular(self):
        self.assertEqual(number_to_string(5.61, decimal_digits=2), "5.61")

    def test_number_to_string_value_replacement_not_used(self):
        self.assertEqual(number_to_string(4.41, decimal_digits=2, replacement="-"), "4.41")

    def test_number_to_string_no_value_replacement_used(self):
        self.assertEqual(number_to_string(None, replacement="Heureka"), "Heureka")

    def test_number_to_string_value_greater_thousand(self):
        self.assertEqual(number_to_string(1234.56, decimal_digits=2), "1,234.56")

    def test_number_to_string_int_value_no_digits(self):
        self.assertEqual(number_to_string(117), "117")

    def test_number_to_string_int_value_with_digits(self):
        self.assertEqual(number_to_string(117, decimal_digits=2), "117.00")

    def test_string_or_none_to_string_regular(self):
        my_str = "I am a string."
        self.assertEqual(string_or_none_to_string(my_str), my_str)

    def test_string_or_none_to_string_replacement_undefined(self):
        self.assertEqual(string_or_none_to_string(None), "-")

    def test_string_or_none_to_string_replacement_defined(self):
        self.assertEqual(string_or_none_to_string(None, "no value"), "no value")

    def test_encode_to_xml_regular(self):
        xml_str = "<tag>Something with an ampersand (&)</tag>"
        self.assertEqual(encode_to_xml(xml_str), "&lt;tag&gt;Something with an ampersand (&amp;)&lt;/tag&gt;")
