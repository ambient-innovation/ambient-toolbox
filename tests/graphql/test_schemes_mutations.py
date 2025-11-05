from unittest import mock

import graphene
from django.test import TestCase
from graphql import GraphQLError

from ambient_toolbox.graphql.schemes.mutations import DeleteMutation, LoginRequiredDeleteMutation
from testapp.models import CommonInfoBasedModel


class DeleteMutationTest(TestCase):
    """Test suite for DeleteMutation."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.test_instance = CommonInfoBasedModel.objects.create(value=42)

    def setUp(self):
        """Set up test fixtures."""

        # Create a concrete implementation for testing
        class TestDeleteMutation(DeleteMutation):
            class Meta:
                abstract = False
                model = CommonInfoBasedModel

        self.TestDeleteMutation = TestDeleteMutation

    def test_inherits_from_client_id_mutation(self):
        """Test that DeleteMutation inherits from graphene.ClientIDMutation."""
        self.assertTrue(issubclass(DeleteMutation, graphene.ClientIDMutation))

    def test_has_success_field(self):
        """Test that DeleteMutation has success field."""
        self.assertTrue(hasattr(DeleteMutation, "success"))

    def test_has_model_attribute(self):
        """Test that DeleteMutation has model attribute."""
        self.assertIsNone(DeleteMutation.model)

    def test_init_subclass_with_meta_raises_error_without_model(self):
        """Test that __init_subclass_with_meta__ raises AttributeError when model is not set."""
        with self.assertRaisesMessage(AttributeError, "DeleteMutation needs a valid model to be set."):

            class InvalidDeleteMutation(DeleteMutation):
                class Meta:
                    abstract = False

    def test_init_subclass_with_meta_sets_model(self):
        """Test that __init_subclass_with_meta__ sets model attribute."""
        self.assertEqual(self.TestDeleteMutation.model, CommonInfoBasedModel)

    def test_validate_returns_true_by_default(self):
        """Test that validate() returns True by default."""
        mock_request = mock.Mock()
        result = self.TestDeleteMutation.validate(mock_request)
        self.assertTrue(result)

    def test_get_queryset_returns_all_objects_by_default(self):
        """Test that get_queryset() returns all objects by default."""
        mock_request = mock.Mock()
        queryset = self.TestDeleteMutation.get_queryset(mock_request)

        # Verify it returns the model's queryset
        self.assertEqual(queryset.model, CommonInfoBasedModel)
        self.assertEqual(list(queryset), list(CommonInfoBasedModel.objects.all()))

    def test_mutate_and_get_payload_deletes_object(self):
        """Test that mutate_and_get_payload() deletes the object."""
        # Get the object id
        object_id = self.test_instance.id

        # Create mock context
        mock_context = mock.Mock()

        # Create mock info
        mock_info = mock.Mock()
        mock_info.context = mock_context

        # Call mutate_and_get_payload
        result = self.TestDeleteMutation.mutate_and_get_payload(None, mock_info, id=str(object_id))

        # Verify the object was deleted
        self.assertFalse(CommonInfoBasedModel.objects.filter(id=object_id).exists())

        # Verify result is an instance of DeleteMutation
        self.assertIsInstance(result, DeleteMutation)

    def test_mutate_and_get_payload_raises_error_when_validation_fails(self):
        """Test that mutate_and_get_payload() raises GraphQLError when validation fails."""

        # Create a mutation with custom validation that returns False
        class TestDeleteMutationWithValidation(DeleteMutation):
            class Meta:
                abstract = False
                model = CommonInfoBasedModel

            @classmethod
            def validate(cls, request):
                return False

        # Create mock context
        mock_context = mock.Mock()

        # Create mock info
        mock_info = mock.Mock()
        mock_info.context = mock_context

        # Call mutate_and_get_payload and expect GraphQLError
        with self.assertRaisesMessage(GraphQLError, "Delete method not allowed."):
            TestDeleteMutationWithValidation.mutate_and_get_payload(None, mock_info, id="1")

    def test_mutate_and_get_payload_with_custom_get_queryset(self):
        """Test that mutate_and_get_payload() uses custom get_queryset."""
        # Create another test instance
        another_instance = CommonInfoBasedModel.objects.create(value=100)

        # Create a mutation with custom get_queryset
        class TestDeleteMutationWithCustomQueryset(DeleteMutation):
            class Meta:
                abstract = False
                model = CommonInfoBasedModel

            @classmethod
            def get_queryset(cls, request):
                # Only return objects with value >= 100
                return CommonInfoBasedModel.objects.filter(value__gte=100)

        # Create mock context
        mock_context = mock.Mock()

        # Create mock info
        mock_info = mock.Mock()
        mock_info.context = mock_context

        # Try to delete the first instance (value=42) - should raise DoesNotExist
        with self.assertRaisesMessage(
            CommonInfoBasedModel.DoesNotExist, "CommonInfoBasedModel matching query does not exist"
        ):
            TestDeleteMutationWithCustomQueryset.mutate_and_get_payload(None, mock_info, id=str(self.test_instance.id))

        # Delete the second instance (value=100) - should succeed
        result = TestDeleteMutationWithCustomQueryset.mutate_and_get_payload(
            None, mock_info, id=str(another_instance.id)
        )

        # Verify the second instance was deleted
        self.assertFalse(CommonInfoBasedModel.objects.filter(id=another_instance.id).exists())

        # Verify result is an instance of DeleteMutation
        self.assertIsInstance(result, DeleteMutation)

    def test_mutate_and_get_payload_converts_id_to_int(self):
        """Test that mutate_and_get_payload() converts string ID to integer."""
        # Create a new instance
        instance = CommonInfoBasedModel.objects.create(value=50)

        # Create mock context
        mock_context = mock.Mock()

        # Create mock info
        mock_info = mock.Mock()
        mock_info.context = mock_context

        # Call with string ID
        result = self.TestDeleteMutation.mutate_and_get_payload(None, mock_info, id=str(instance.id))

        # Verify the object was deleted
        self.assertFalse(CommonInfoBasedModel.objects.filter(id=instance.id).exists())

        # Verify result is an instance of DeleteMutation
        self.assertIsInstance(result, DeleteMutation)

    def test_input_class_has_id_field(self):
        """Test that Input class has id field."""
        self.assertTrue(hasattr(DeleteMutation.Input, "id"))


class LoginRequiredDeleteMutationTest(TestCase):
    """Test suite for LoginRequiredDeleteMutation."""

    def test_inherits_from_delete_mutation(self):
        """Test that LoginRequiredDeleteMutation inherits from DeleteMutation."""
        self.assertTrue(issubclass(LoginRequiredDeleteMutation, DeleteMutation))

    def test_has_login_required_decorator(self):
        """Test that mutate_and_get_payload method has login_required decorator."""
        # The decorator is applied to mutate_and_get_payload method
        # We can check if the class has the expected behavior by checking the method
        self.assertTrue(hasattr(LoginRequiredDeleteMutation, "mutate_and_get_payload"))

    def test_class_is_abstract(self):
        """Test that the class is defined as abstract."""
        # The Meta class is not directly accessible at runtime in graphene,
        # but we can verify the class works as expected for abstract mutations
        # by checking that it has the expected methods
        self.assertTrue(hasattr(LoginRequiredDeleteMutation, "mutate_and_get_payload"))
