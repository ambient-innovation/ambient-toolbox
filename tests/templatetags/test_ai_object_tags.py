from unittest.mock import Mock

from django.test import TestCase

from ambient_toolbox.templatetags.ai_object_tags import dict_key_lookup, label


class AiObjectTagTest(TestCase):
    def test_dict_key_lookup_existing_key(self):
        """Test dict_key_lookup with existing key"""
        test_dict = {"key1": "value1", "key2": "value2"}
        result = dict_key_lookup(test_dict, "key1")
        self.assertEqual(result, "value1")

    def test_dict_key_lookup_missing_key(self):
        """Test dict_key_lookup with missing key returns empty string"""
        test_dict = {"key1": "value1"}
        result = dict_key_lookup(test_dict, "nonexistent")
        self.assertEqual(result, "")

    def test_dict_key_lookup_empty_dict(self):
        """Test dict_key_lookup with empty dictionary"""
        test_dict = {}
        result = dict_key_lookup(test_dict, "anykey")
        self.assertEqual(result, "")

    def test_dict_key_lookup_none_value(self):
        """Test dict_key_lookup where the value is None"""
        test_dict = {"key1": None}
        result = dict_key_lookup(test_dict, "key1")
        self.assertIsNone(result)

    def test_dict_key_lookup_integer_key(self):
        """Test dict_key_lookup with integer key"""
        test_dict = {1: "value1", 2: "value2"}
        result = dict_key_lookup(test_dict, 1)
        self.assertEqual(result, "value1")

    def test_dict_key_lookup_complex_value(self):
        """Test dict_key_lookup with complex value (list, dict)"""
        test_dict = {"key1": [1, 2, 3], "key2": {"nested": "dict"}}
        result = dict_key_lookup(test_dict, "key1")
        self.assertEqual(result, [1, 2, 3])

    def test_label_filter(self):
        """Test label filter returns field class name"""
        # Create a mock form field with a field attribute
        mock_bound_field = Mock()
        mock_field = Mock()
        mock_field.__class__.__name__ = "CharField"
        mock_bound_field.field = mock_field

        result = label(mock_bound_field)
        self.assertEqual(result, "CharField")

    def test_label_filter_different_field_types(self):
        """Test label filter with different field types"""
        # Test with EmailField
        mock_bound_field = Mock()
        mock_field = Mock()
        mock_field.__class__.__name__ = "EmailField"
        mock_bound_field.field = mock_field

        result = label(mock_bound_field)
        self.assertEqual(result, "EmailField")

        # Test with IntegerField
        mock_field.__class__.__name__ = "IntegerField"
        result = label(mock_bound_field)
        self.assertEqual(result, "IntegerField")
