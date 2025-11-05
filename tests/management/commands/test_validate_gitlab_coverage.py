from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase


class ValidateGitlabCoverageCommandTest(SimpleTestCase):
    """Test cases for validate_gitlab_coverage management command."""

    @mock.patch("ambient_toolbox.management.commands.validate_gitlab_coverage.CoverageService")
    def test_management_command_calls_coverage_service(self, mock_coverage_service_class):
        """Test that the command calls CoverageService.process()."""
        mock_service_instance = mock.MagicMock()
        mock_coverage_service_class.return_value = mock_service_instance
        mock_service_instance.process.return_value = None

        call_command("validate_gitlab_coverage")

        mock_coverage_service_class.assert_called_once_with()
        mock_service_instance.process.assert_called_once_with()

    @mock.patch("ambient_toolbox.management.commands.validate_gitlab_coverage.CoverageService")
    def test_management_command_returns_process_result(self, mock_coverage_service_class):
        """Test that the command returns the result from process()."""
        mock_service_instance = mock.MagicMock()
        mock_coverage_service_class.return_value = mock_service_instance
        mock_service_instance.process.return_value = "some_value"

        result = call_command("validate_gitlab_coverage")

        self.assertEqual(result, "some_value")
        mock_service_instance.process.assert_called_once_with()

    @mock.patch("ambient_toolbox.management.commands.validate_gitlab_coverage.CoverageService")
    def test_management_command_propagates_exceptions(self, mock_coverage_service_class):
        """Test that exceptions from CoverageService.process() are propagated."""
        mock_service_instance = mock.MagicMock()
        mock_coverage_service_class.return_value = mock_service_instance
        mock_service_instance.process.side_effect = Exception("Coverage validation failed")

        with self.assertRaises(Exception) as cm:
            call_command("validate_gitlab_coverage")

        self.assertEqual(str(cm.exception), "Coverage validation failed")
        mock_service_instance.process.assert_called_once_with()
