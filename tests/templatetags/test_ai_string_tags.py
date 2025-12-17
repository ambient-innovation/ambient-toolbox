from django.test import TestCase

from ambient_toolbox.templatetags.ai_string_tags import concat, get_first_char, trim


class AiStringTagTest(TestCase):
    def test_get_first_char_normal_string(self):
        """Test get_first_char with normal string"""
        result = get_first_char("hello")
        self.assertEqual(result, "h")

    def test_get_first_char_single_char(self):
        """Test get_first_char with single character"""
        result = get_first_char("a")
        self.assertEqual(result, "a")

    def test_get_first_char_empty_string(self):
        """Test get_first_char with empty string"""
        result = get_first_char("")
        self.assertEqual(result, "")

    def test_get_first_char_whitespace(self):
        """Test get_first_char with whitespace"""
        result = get_first_char(" hello")
        self.assertEqual(result, " ")

    def test_get_first_char_unicode(self):
        """Test get_first_char with unicode characters"""
        result = get_first_char("über")
        self.assertEqual(result, "ü")

    def test_concat_two_strings(self):
        """Test concat with two strings"""
        result = concat("hello", " world")
        self.assertEqual(result, "hello world")

    def test_concat_with_empty_string(self):
        """Test concat with empty string"""
        result = concat("hello", "")
        self.assertEqual(result, "hello")

    def test_concat_both_empty(self):
        """Test concat with both empty strings"""
        result = concat("", "")
        self.assertEqual(result, "")

    def test_concat_with_numbers(self):
        """Test concat with numbers (converted to strings)"""
        result = concat(123, 456)
        self.assertEqual(result, "123456")

    def test_concat_mixed_types(self):
        """Test concat with mixed types"""
        result = concat("Number: ", 42)
        self.assertEqual(result, "Number: 42")

    def test_concat_with_none(self):
        """Test concat with None value"""
        result = concat("hello", " None")
        self.assertEqual(result, "hello None")

    def test_trim_with_whitespace(self):
        """Test trim with leading and trailing whitespace"""
        result = trim("  hello  ")
        self.assertEqual(result, "hello")

    def test_trim_leading_whitespace(self):
        """Test trim with only leading whitespace"""
        result = trim("  hello")
        self.assertEqual(result, "hello")

    def test_trim_trailing_whitespace(self):
        """Test trim with only trailing whitespace"""
        result = trim("hello  ")
        self.assertEqual(result, "hello")

    def test_trim_no_whitespace(self):
        """Test trim with no whitespace"""
        result = trim("hello")
        self.assertEqual(result, "hello")

    def test_trim_only_whitespace(self):
        """Test trim with only whitespace"""
        result = trim("   ")
        self.assertEqual(result, "")

    def test_trim_tabs_and_newlines(self):
        """Test trim with tabs and newlines"""
        result = trim("\t\nhello\n\t")
        self.assertEqual(result, "hello")

    def test_trim_internal_whitespace_preserved(self):
        """Test trim preserves internal whitespace"""
        result = trim("  hello world  ")
        self.assertEqual(result, "hello world")
