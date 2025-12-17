from unittest import mock

from django.test import TestCase

from ambient_toolbox.graphql.sentry.utils import ignore_graphene_logger


class IgnoreGrapheneLoggerTest(TestCase):
    """Test suite for ignore_graphene_logger utility function."""

    @mock.patch("ambient_toolbox.graphql.sentry.utils.ignore_logger")
    def test_ignore_graphene_logger_calls_ignore_logger_with_correct_logger_name(self, mock_ignore_logger):
        """Test that ignore_graphene_logger() calls ignore_logger with correct logger name."""
        ignore_graphene_logger()

        # Verify ignore_logger was called with the correct logger name
        mock_ignore_logger.assert_called_once_with("graphql.execution.utils")

    @mock.patch("ambient_toolbox.graphql.sentry.utils.ignore_logger")
    def test_ignore_graphene_logger_returns_none(self, mock_ignore_logger):
        """Test that ignore_graphene_logger() returns None."""
        result = ignore_graphene_logger()

        # Verify result is None
        self.assertIsNone(result)
