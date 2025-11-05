from unittest.mock import Mock, patch

import graphene
from django.test import TestCase
from graphene_django.views import GraphQLView

from ambient_toolbox.graphql.sentry.views import SentryGraphQLView


class SentryGraphQLViewTest(TestCase):
    """Test suite for SentryGraphQLView."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()

        # Create a simple schema for testing
        class Query(graphene.ObjectType):
            hello = graphene.String()

            def resolve_hello(self, info):
                return "World"

        cls.test_schema = graphene.Schema(query=Query)

    def test_inherits_from_graphql_view(self):
        """Test that SentryGraphQLView inherits from GraphQLView."""
        self.assertTrue(issubclass(SentryGraphQLView, GraphQLView))

    @patch.object(GraphQLView, "execute_graphql_request")
    def test_execute_graphql_request_without_errors(self, mock_super_execute):
        """Test execute_graphql_request() returns result without calling _capture_sentry_exceptions when no errors."""
        # Mock result without errors
        mock_result = Mock()
        mock_result.errors = None
        mock_super_execute.return_value = mock_result

        # Create view instance with schema
        view = SentryGraphQLView(schema=self.test_schema)

        # Patch _capture_sentry_exceptions to verify it's not called
        with patch.object(view, "_capture_sentry_exceptions") as mock_capture:
            result = view.execute_graphql_request("arg1", "arg2", kwarg1="value1")

            # Verify super().execute_graphql_request was called with correct arguments
            mock_super_execute.assert_called_once_with("arg1", "arg2", kwarg1="value1")

            # Verify _capture_sentry_exceptions was not called
            mock_capture.assert_not_called()

            # Verify result is returned
            self.assertEqual(result, mock_result)

    @patch.object(GraphQLView, "execute_graphql_request")
    def test_execute_graphql_request_with_errors(self, mock_super_execute):
        """Test that execute_graphql_request() calls _capture_sentry_exceptions when errors are present."""
        # Mock errors
        mock_error_1 = Mock()
        mock_error_2 = Mock()

        # Mock result with errors
        mock_result = Mock()
        mock_result.errors = [mock_error_1, mock_error_2]
        mock_super_execute.return_value = mock_result

        # Create view instance with schema
        view = SentryGraphQLView(schema=self.test_schema)

        # Patch _capture_sentry_exceptions
        with patch.object(view, "_capture_sentry_exceptions") as mock_capture:
            result = view.execute_graphql_request("arg1", "arg2", kwarg1="value1")

            # Verify super().execute_graphql_request was called
            mock_super_execute.assert_called_once_with("arg1", "arg2", kwarg1="value1")

            # Verify _capture_sentry_exceptions was called with errors
            mock_capture.assert_called_once_with([mock_error_1, mock_error_2])

            # Verify result is returned
            self.assertEqual(result, mock_result)

    @patch.object(GraphQLView, "execute_graphql_request")
    def test_execute_graphql_request_with_empty_errors_list(self, mock_super_execute):
        """Test that execute_graphql_request() does not call _capture_sentry_exceptions with empty errors list."""
        # Mock result with empty errors list
        mock_result = Mock()
        mock_result.errors = []
        mock_super_execute.return_value = mock_result

        # Create view instance with schema
        view = SentryGraphQLView(schema=self.test_schema)

        # Patch _capture_sentry_exceptions
        with patch.object(view, "_capture_sentry_exceptions") as mock_capture:
            result = view.execute_graphql_request()

            # Verify _capture_sentry_exceptions was NOT called because empty list is falsy
            mock_capture.assert_not_called()

            # Verify result is returned
            self.assertEqual(result, mock_result)

    @patch("ambient_toolbox.graphql.sentry.views.sentry_sdk")
    def test_capture_sentry_exceptions_with_original_error(self, mock_sentry_sdk):
        """Test that _capture_sentry_exceptions() captures original_error from errors."""
        # Mock error with original_error attribute
        mock_original_error = Exception("Original error")
        mock_error = Mock()
        mock_error.original_error = mock_original_error

        # Create view instance with schema
        view = SentryGraphQLView(schema=self.test_schema)

        # Call _capture_sentry_exceptions
        view._capture_sentry_exceptions([mock_error])

        # Verify sentry_sdk.capture_exception was called with original_error
        mock_sentry_sdk.capture_exception.assert_called_once_with(mock_original_error)

    @patch("ambient_toolbox.graphql.sentry.views.sentry_sdk")
    def test_capture_sentry_exceptions_without_original_error(self, mock_sentry_sdk):
        """Test that _capture_sentry_exceptions() captures error itself when no original_error."""
        # Mock error without original_error attribute
        mock_error = Mock(spec=[])  # spec=[] means no attributes
        # Make sure accessing original_error raises AttributeError
        type(mock_error).original_error = property(lambda self: (_ for _ in ()).throw(AttributeError("no attribute")))

        # Create view instance with schema
        view = SentryGraphQLView(schema=self.test_schema)

        # Call _capture_sentry_exceptions
        view._capture_sentry_exceptions([mock_error])

        # Verify sentry_sdk.capture_exception was called with the error itself
        mock_sentry_sdk.capture_exception.assert_called_once_with(mock_error)

    @patch("ambient_toolbox.graphql.sentry.views.sentry_sdk")
    def test_capture_sentry_exceptions_with_multiple_errors(self, mock_sentry_sdk):
        """Test that _capture_sentry_exceptions() captures all errors in the list."""
        # Mock multiple errors
        mock_original_error_1 = Exception("Original error 1")
        mock_error_1 = Mock()
        mock_error_1.original_error = mock_original_error_1

        mock_original_error_2 = Exception("Original error 2")
        mock_error_2 = Mock()
        mock_error_2.original_error = mock_original_error_2

        # Create view instance with schema
        view = SentryGraphQLView(schema=self.test_schema)

        # Call _capture_sentry_exceptions
        view._capture_sentry_exceptions([mock_error_1, mock_error_2])

        # Verify sentry_sdk.capture_exception was called twice
        self.assertEqual(mock_sentry_sdk.capture_exception.call_count, 2)
        mock_sentry_sdk.capture_exception.assert_any_call(mock_original_error_1)
        mock_sentry_sdk.capture_exception.assert_any_call(mock_original_error_2)

    @patch("ambient_toolbox.graphql.sentry.views.sentry_sdk")
    def test_capture_sentry_exceptions_with_mixed_errors(self, mock_sentry_sdk):
        """Test that _capture_sentry_exceptions() handles mix of errors with and without original_error."""
        # Mock error with original_error
        mock_original_error = Exception("Original error")
        mock_error_1 = Mock()
        mock_error_1.original_error = mock_original_error

        # Mock error without original_error
        mock_error_2 = Mock(spec=[])
        type(mock_error_2).original_error = property(lambda self: (_ for _ in ()).throw(AttributeError("no attribute")))

        # Create view instance with schema
        view = SentryGraphQLView(schema=self.test_schema)

        # Call _capture_sentry_exceptions
        view._capture_sentry_exceptions([mock_error_1, mock_error_2])

        # Verify sentry_sdk.capture_exception was called twice
        self.assertEqual(mock_sentry_sdk.capture_exception.call_count, 2)
        mock_sentry_sdk.capture_exception.assert_any_call(mock_original_error)
        mock_sentry_sdk.capture_exception.assert_any_call(mock_error_2)
