from django.test import TestCase

from ambient_toolbox.templatetags.ai_number_tags import multiply


class AiNumberTagTest(TestCase):
    def test_multiply_regular(self):
        self.assertEqual(multiply(3, 3), 9)

    def test_multiply_string(self):
        self.assertEqual(multiply("3", 3), 9)

    def test_multiply_german_float(self):
        self.assertEqual(multiply("3,19", 3), 9.57)

    def test_multiply_no_value(self):
        self.assertIsNone(multiply(None, 3))
