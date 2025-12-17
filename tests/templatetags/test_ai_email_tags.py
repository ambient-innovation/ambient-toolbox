from django.test import TestCase
from django.utils.safestring import SafeString

from ambient_toolbox.templatetags.ai_email_tags import obfuscate, obfuscate_mailto, obfuscate_string


class AiEmailTagTest(TestCase):
    def test_obfuscate_string_simple(self):
        """Test obfuscate_string with simple text"""
        result = obfuscate_string("test")
        self.assertEqual(result, "&#116;&#101;&#115;&#116;")

    def test_obfuscate_string_email(self):
        """Test obfuscate_string with email address"""
        result = obfuscate_string("test@example.com")
        expected = "&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;"
        self.assertEqual(result, expected)

    def test_obfuscate_string_special_characters(self):
        """Test obfuscate_string with special characters"""
        result = obfuscate_string("a@b.c")
        # @ is 64, . is 46
        self.assertIn("&#64;", result)
        self.assertIn("&#46;", result)

    def test_obfuscate_string_empty(self):
        """Test obfuscate_string with empty string"""
        result = obfuscate_string("")
        self.assertEqual(result, "")

    def test_obfuscate_filter(self):
        """Test obfuscate filter returns SafeString"""
        result = obfuscate("test@example.com")
        self.assertIsInstance(result, SafeString)
        self.assertIn("&#116;", result)

    def test_obfuscate_filter_marks_safe(self):
        """Test obfuscate filter marks the result as safe"""
        result = obfuscate("test")
        self.assertIsInstance(result, SafeString)

    def test_obfuscate_mailto_without_text(self):
        """Test obfuscate_mailto without custom text (text=False)"""
        result = obfuscate_mailto("test@example.com", text=False)
        self.assertIsInstance(result, SafeString)
        # Should contain the obfuscated mailto: prefix
        self.assertIn("&#109;&#97;&#105;&#108;&#116;&#111;&#58;", result)
        # Should contain <a href=
        self.assertIn('<a href="', result)
        # Should contain the email as link text (obfuscated)
        self.assertIn("&#116;&#101;&#115;&#116;", result)

    def test_obfuscate_mailto_with_text(self):
        """Test obfuscate_mailto with custom text"""
        result = obfuscate_mailto("test@example.com", text="Click here")
        self.assertIsInstance(result, SafeString)
        # Should contain the custom text as link text
        self.assertIn("Click here", result)
        # Should still contain the obfuscated email in href
        self.assertIn("&#116;&#101;&#115;&#116;", result)

    def test_obfuscate_mailto_default_text_parameter(self):
        """Test obfuscate_mailto with default text parameter (False)"""
        # When text is False (default), email should be used as link text
        result = obfuscate_mailto("a@b.com")
        # Link text should be the obfuscated email
        self.assertIn("&#97;&#64;&#98;&#46;&#99;&#111;&#109;", result)

    def test_obfuscate_mailto_structure(self):
        """Test obfuscate_mailto produces valid HTML structure"""
        result = obfuscate_mailto("test@example.com", text="Email me")
        # Should have proper HTML structure
        self.assertTrue(result.startswith('<a href="'))
        self.assertTrue(result.endswith("</a>"))
        self.assertIn(">Email me</a>", result)
