from django.test import TestCase
from freezegun import freeze_time

from ambient_toolbox.templatetags.ai_helper_tags import js_versiontag


class AiHelperTagTest(TestCase):
    @freeze_time("2020-06-26 12:30:45.123456")
    def test_js_versiontag_format(self):
        """Test js_versiontag returns correct format"""
        result = js_versiontag()
        self.assertTrue(result.startswith("?s="))
        self.assertEqual(result, "?s=123456")

    @freeze_time("2020-06-26 12:30:45.000000")
    def test_js_versiontag_zero_microseconds(self):
        """Test js_versiontag with zero microseconds"""
        result = js_versiontag()
        self.assertEqual(result, "?s=0")

    @freeze_time("2020-06-26 12:30:45.999999")
    def test_js_versiontag_max_microseconds(self):
        """Test js_versiontag with maximum microseconds"""
        result = js_versiontag()
        self.assertEqual(result, "?s=999999")

    def test_js_versiontag_returns_string(self):
        """Test js_versiontag returns a string"""
        result = js_versiontag()
        self.assertIsInstance(result, str)

    def test_js_versiontag_format_structure(self):
        """Test js_versiontag has correct structure"""
        result = js_versiontag()
        # Should start with ?s=
        self.assertTrue(result.startswith("?s="))
        # Should have a numeric value after ?s=
        value = result[3:]  # Get the part after "?s="
        self.assertTrue(value.isdigit())
