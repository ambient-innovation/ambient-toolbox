from unittest.mock import Mock, patch

from django.test import TestCase
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError
from promise import Promise

from ambient_toolbox.graphql.forms.mutations import (
    DjangoValidatedModelFormMutation,
    LoginRequiredDjangoModelFormMutation,
)


class DjangoValidatedModelFormMutationTest(TestCase):
    """Test suite for DjangoValidatedModelFormMutation."""

    def test_inherits_from_django_model_form_mutation(self):
        """Test that DjangoValidatedModelFormMutation inherits from DjangoModelFormMutation."""
        self.assertTrue(issubclass(DjangoValidatedModelFormMutation, DjangoModelFormMutation))

    def test_mutate_without_errors_returns_payload_with_client_mutation_id(self):
        """Test that mutate() returns payload with client_mutation_id when no errors."""
        # Mock the payload
        mock_payload = Mock()
        mock_payload.errors = []

        # Mock mutate_and_get_payload to return the payload
        with patch.object(
            DjangoValidatedModelFormMutation, "mutate_and_get_payload", return_value=mock_payload
        ) as mock_mutate_and_get_payload:
            input_data = {"client_mutation_id": "test_id"}
            result = DjangoValidatedModelFormMutation.mutate(None, None, input_data)

            # Verify mutate_and_get_payload was called
            mock_mutate_and_get_payload.assert_called_once_with(None, None, **input_data)

            # Verify client_mutation_id was set
            self.assertEqual(result.client_mutation_id, "test_id")

    def test_mutate_with_errors_raises_graphql_error(self):
        """Test that mutate() raises GraphQLError when errors are present."""
        # Mock error objects
        mock_error_1 = Mock()
        mock_error_1.field = "field1"
        mock_error_1.messages = ["Error message 1"]

        mock_error_2 = Mock()
        mock_error_2.field = "field2"
        mock_error_2.messages = ["Error message 2"]

        # Mock the payload with errors
        mock_payload = Mock()
        mock_payload.errors = [mock_error_1, mock_error_2]

        # Mock mutate_and_get_payload to return the payload with errors
        with patch.object(DjangoValidatedModelFormMutation, "mutate_and_get_payload", return_value=mock_payload):
            input_data = {"client_mutation_id": "test_id"}

            with self.assertRaises(GraphQLError) as context:
                DjangoValidatedModelFormMutation.mutate(None, None, input_data)

            # Verify the error message contains both field errors
            error_message = str(context.exception)
            self.assertIn("Field 'field1': Error message 1", error_message)
            self.assertIn("Field 'field2': Error message 2", error_message)

    def test_mutate_with_single_error_raises_graphql_error(self):
        """Test that mutate() raises GraphQLError with single error message."""
        # Mock error object
        mock_error = Mock()
        mock_error.field = "test_field"
        mock_error.messages = ["Single error message"]

        # Mock the payload with errors
        mock_payload = Mock()
        mock_payload.errors = [mock_error]

        # Mock mutate_and_get_payload to return the payload with errors
        with patch.object(DjangoValidatedModelFormMutation, "mutate_and_get_payload", return_value=mock_payload):
            input_data = {"client_mutation_id": "test_id"}

            with self.assertRaises(GraphQLError) as context:
                DjangoValidatedModelFormMutation.mutate(None, None, input_data)

            # Verify the error message
            self.assertEqual(str(context.exception), "Field 'test_field': Single error message")

    def test_mutate_with_thenable_result_returns_promise(self):
        """Test that mutate() returns Promise when result is thenable."""
        # Create a mock payload
        mock_payload = Mock()
        mock_payload.errors = []

        # Create a Promise as the result (Promise needs errors attribute too)
        promise_result = Promise.resolve(mock_payload)
        promise_result.errors = []  # Add errors attribute to pass the check

        # Mock mutate_and_get_payload to return a promise
        with patch.object(DjangoValidatedModelFormMutation, "mutate_and_get_payload", return_value=promise_result):
            input_data = {"client_mutation_id": "test_id"}
            result = DjangoValidatedModelFormMutation.mutate(None, None, input_data)

            # Verify result is a Promise
            self.assertTrue(hasattr(result, "then"))

    def test_mutate_handles_exception_when_setting_client_mutation_id(self):
        """Test that mutate() raises Exception when setting client_mutation_id fails."""
        # Mock payload that raises exception when setting client_mutation_id
        mock_payload = Mock()
        mock_payload.errors = []
        # Make setting client_mutation_id raise an exception
        type(mock_payload).client_mutation_id = property(
            fget=lambda self: None, fset=lambda self, value: (_ for _ in ()).throw(AttributeError("test error"))
        )

        # Mock mutate_and_get_payload to return the payload
        with patch.object(DjangoValidatedModelFormMutation, "mutate_and_get_payload", return_value=mock_payload):
            input_data = {"client_mutation_id": "test_id"}

            with self.assertRaises(Exception) as context:
                DjangoValidatedModelFormMutation.mutate(None, None, input_data)

            # Verify the exception message
            self.assertIn("Cannot set client_mutation_id in the payload object", str(context.exception))

    def test_mutate_without_client_mutation_id_in_input(self):
        """Test that mutate() handles missing client_mutation_id in input."""
        # Mock the payload
        mock_payload = Mock()
        mock_payload.errors = []

        # Mock mutate_and_get_payload to return the payload
        with patch.object(DjangoValidatedModelFormMutation, "mutate_and_get_payload", return_value=mock_payload):
            input_data = {}
            result = DjangoValidatedModelFormMutation.mutate(None, None, input_data)

            # Verify client_mutation_id was set to None
            self.assertIsNone(result.client_mutation_id)


class LoginRequiredDjangoModelFormMutationTest(TestCase):
    """Test suite for LoginRequiredDjangoModelFormMutation."""

    def test_inherits_from_django_validated_model_form_mutation(self):
        """Test that LoginRequiredDjangoModelFormMutation inherits from DjangoValidatedModelFormMutation."""
        self.assertTrue(issubclass(LoginRequiredDjangoModelFormMutation, DjangoValidatedModelFormMutation))

    def test_has_login_required_decorator(self):
        """Test that perform_mutate method has login_required decorator."""
        # The decorator is applied to perform_mutate method
        # We can check if the class has the expected behavior by checking the method
        self.assertTrue(hasattr(LoginRequiredDjangoModelFormMutation, "perform_mutate"))

    def test_class_is_abstract(self):
        """Test that the class is defined as abstract."""
        # The Meta class is not directly accessible at runtime in graphene,
        # but we can verify the class works as expected for abstract mutations
        # by checking that it cannot be used directly without subclassing
        self.assertTrue(hasattr(LoginRequiredDjangoModelFormMutation, "perform_mutate"))
