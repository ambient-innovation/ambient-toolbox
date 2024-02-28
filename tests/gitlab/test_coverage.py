from unittest import mock

from django.test import SimpleTestCase

from ambient_toolbox.gitlab.coverage import CoverageService


@mock.patch.dict("os.environ", {"CI_PIPELINE_ID": "17", "CI_PROJECT_ID": "27"})
class CoverageServiceTest(SimpleTestCase):
    def test_get_disable_coverage_integer_false(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="0")

        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_get_disable_coverage_integer_true(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="1")

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_get_disable_coverage_string_var_bool_false(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="False")

        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_get_disable_coverage_string_var_bool_true(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="True")

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_get_disable_coverage_string_var_random(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="Wololo")

        self.assertIsInstance(result, bool)
        self.assertTrue(result)
