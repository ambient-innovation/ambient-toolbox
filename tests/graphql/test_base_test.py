import json
from unittest import mock

from django.test import TestCase

from ambient_toolbox.graphql.tests.base_test import GraphQLTestCase


class GraphQLTestCaseTest(TestCase):
    """Test suite for GraphQLTestCase."""

    def test_inherits_from_test_case(self):
        """Test that GraphQLTestCase inherits from TestCase."""
        self.assertTrue(issubclass(GraphQLTestCase, TestCase))

    def test_default_graphql_url(self):
        """Test that GRAPHQL_URL has the correct default value."""
        self.assertEqual(GraphQLTestCase.GRAPHQL_URL, "/graphql/")

    def test_default_graphql_schema_is_none(self):
        """Test that GRAPHQL_SCHEMA is None by default."""
        self.assertIsNone(GraphQLTestCase.GRAPHQL_SCHEMA)

    def test_setup_class_raises_error_when_schema_not_defined(self):
        """Test that setUpClass() raises AttributeError when GRAPHQL_SCHEMA is not defined."""

        class TestGraphQLTestCaseWithoutSchema(GraphQLTestCase):
            pass

        with self.assertRaisesMessage(AttributeError, "Variable GRAPHQL_SCHEMA not defined in GraphQLTestCase."):
            TestGraphQLTestCaseWithoutSchema.setUpClass()

    @mock.patch.object(TestCase, "setUpClass")
    def test_setup_class_creates_client_with_schema(self, mock_super_setup):
        """Test that setUpClass() creates a Client with the GRAPHQL_SCHEMA."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Mock the Client constructor
        with mock.patch("ambient_toolbox.graphql.tests.base_test.Client") as mock_client_class:
            mock_client_instance = mock.Mock()
            mock_client_class.return_value = mock_client_instance

            TestGraphQLTestCaseWithSchema.setUpClass()

            # Verify super().setUpClass() was called
            mock_super_setup.assert_called_once()

            # Verify Client was instantiated with the schema
            mock_client_class.assert_called_once_with(mock_schema)

            # Verify _client was set
            self.assertEqual(TestGraphQLTestCaseWithSchema._client, mock_client_instance)

    def test_query_with_all_parameters(self):
        """Test that query() constructs the request body correctly with all parameters."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Create an instance
        test_instance = TestGraphQLTestCaseWithSchema()

        # Mock the _client
        mock_client = mock.Mock()
        mock_response = mock.Mock()
        mock_client.post.return_value = mock_response
        TestGraphQLTestCaseWithSchema._client = mock_client

        # Call query with all parameters
        query_str = "mutation TestMutation { test }"
        op_name = "TestMutation"
        input_data = {"field1": "value1", "field2": "value2"}

        result = test_instance.query(query_str, op_name, input_data)

        # Verify post was called with correct arguments
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args

        # Verify URL
        self.assertEqual(call_args[0][0], "/graphql/")

        # Verify body
        body = json.loads(call_args[0][1])
        self.assertEqual(body["query"], query_str)
        self.assertEqual(body["operation_name"], op_name)
        self.assertEqual(body["variables"]["input"], input_data)

        # Verify content type
        self.assertEqual(call_args[1]["content_type"], "application/json")

        # Verify result
        self.assertEqual(result, mock_response)

    def test_query_with_query_only(self):
        """Test that query() works with only query parameter."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Create an instance
        test_instance = TestGraphQLTestCaseWithSchema()

        # Mock the _client
        mock_client = mock.Mock()
        mock_response = mock.Mock()
        mock_client.post.return_value = mock_response
        TestGraphQLTestCaseWithSchema._client = mock_client

        # Call query with only query parameter
        query_str = "{ allUsers { id } }"

        result = test_instance.query(query_str)

        # Verify post was called
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args

        # Verify body contains only query
        body = json.loads(call_args[0][1])
        self.assertEqual(body["query"], query_str)
        self.assertNotIn("operation_name", body)
        self.assertNotIn("variables", body)

        # Verify result
        self.assertEqual(result, mock_response)

    def test_query_with_query_and_op_name(self):
        """Test that query() works with query and operation name."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Create an instance
        test_instance = TestGraphQLTestCaseWithSchema()

        # Mock the _client
        mock_client = mock.Mock()
        mock_response = mock.Mock()
        mock_client.post.return_value = mock_response
        TestGraphQLTestCaseWithSchema._client = mock_client

        # Call query with query and op_name
        query_str = "mutation TestMutation { test }"
        op_name = "TestMutation"

        result = test_instance.query(query_str, op_name)

        # Verify post was called
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args

        # Verify body
        body = json.loads(call_args[0][1])
        self.assertEqual(body["query"], query_str)
        self.assertEqual(body["operation_name"], op_name)
        self.assertNotIn("variables", body)

        # Verify result
        self.assertEqual(result, mock_response)

    def test_query_with_query_and_input_data(self):
        """Test that query() works with query and input_data."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Create an instance
        test_instance = TestGraphQLTestCaseWithSchema()

        # Mock the _client
        mock_client = mock.Mock()
        mock_response = mock.Mock()
        mock_client.post.return_value = mock_response
        TestGraphQLTestCaseWithSchema._client = mock_client

        # Call query with query and input_data
        query_str = "mutation { createUser(input: $input) { id } }"
        input_data = {"name": "John Doe"}

        result = test_instance.query(query_str, input_data=input_data)

        # Verify post was called
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args

        # Verify body
        body = json.loads(call_args[0][1])
        self.assertEqual(body["query"], query_str)
        self.assertNotIn("operation_name", body)
        self.assertEqual(body["variables"]["input"], input_data)

        # Verify result
        self.assertEqual(result, mock_response)

    def test_assert_response_no_errors_with_valid_response(self):
        """Test that assertResponseNoErrors() passes for valid response."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Create an instance
        test_instance = TestGraphQLTestCaseWithSchema()

        # Mock response without errors
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.content = json.dumps({"data": {"test": "value"}}).encode()

        # Call assertResponseNoErrors - should not raise
        test_instance.assertResponseNoErrors(mock_response)

    def test_assert_response_no_errors_with_error_response(self):
        """Test that assertResponseNoErrors() fails for response with errors."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Create an instance
        test_instance = TestGraphQLTestCaseWithSchema()

        # Mock response with errors
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.content = json.dumps({"errors": [{"message": "Test error"}]}).encode()

        # Call assertResponseNoErrors - should raise AssertionError
        with self.assertRaisesMessage(AssertionError, "'errors' unexpectedly found in"):
            test_instance.assertResponseNoErrors(mock_response)

    def test_assert_response_no_errors_with_non_200_status(self):
        """Test that assertResponseNoErrors() fails for non-200 status."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Create an instance
        test_instance = TestGraphQLTestCaseWithSchema()

        # Mock response with non-200 status
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_response.content = json.dumps({"data": {"test": "value"}}).encode()

        # Call assertResponseNoErrors - should raise AssertionError
        with self.assertRaisesMessage(AssertionError, "500 != 200"):
            test_instance.assertResponseNoErrors(mock_response)

    def test_assert_response_has_errors_with_error_response(self):
        """Test that assertResponseHasErrors() passes for response with errors."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Create an instance
        test_instance = TestGraphQLTestCaseWithSchema()

        # Mock response with errors
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.content = json.dumps({"errors": [{"message": "Test error"}]}).encode()

        # Call assertResponseHasErrors - should not raise
        test_instance.assertResponseHasErrors(mock_response)

    def test_assert_response_has_errors_with_valid_response(self):
        """Test that assertResponseHasErrors() fails for response without errors."""
        mock_schema = mock.Mock()

        class TestGraphQLTestCaseWithSchema(GraphQLTestCase):
            GRAPHQL_SCHEMA = mock_schema

        # Create an instance
        test_instance = TestGraphQLTestCaseWithSchema()

        # Mock response without errors
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.content = json.dumps({"data": {"test": "value"}}).encode()

        # Call assertResponseHasErrors - should raise AssertionError
        with self.assertRaisesMessage(AssertionError, "'errors' not found in"):
            test_instance.assertResponseHasErrors(mock_response)
