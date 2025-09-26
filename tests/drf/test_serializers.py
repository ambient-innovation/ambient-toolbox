from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ambient_toolbox.drf.serializers import BaseModelSerializer, CommonInfoSerializer
from testapp.models import CommonInfoBasedModel

User = get_user_model()


class DummyModelSerializer(BaseModelSerializer):
    class Meta:
        model = CommonInfoBasedModel
        fields = ["value", "value_b"]


class DummyCommonInfoSerializer(CommonInfoSerializer):
    class Meta:
        model = CommonInfoBasedModel
        fields = ["value", "value_b", "created_by", "lastmodified_by"]


class BaseModelSerializerTest(TestCase):
    def setUp(self):
        self.serializer = DummyModelSerializer()
        self.factory = APIRequestFactory()

    def test_validate_calls_model_clean(self):
        """Test that validate calls the model's clean() method"""
        data = {"value": 10, "value_b": 20}

        with patch.object(CommonInfoBasedModel, "clean") as mock_clean:
            result = self.serializer.validate(data)

            mock_clean.assert_called_once()
            self.assertEqual(result, data)

    def test_validate_with_validation_error(self):
        """Test that validate raises ValidationError when model clean fails"""
        data = {"value": 10, "value_b": 20}

        with patch.object(CommonInfoBasedModel, "clean", side_effect=ValidationError("Test error")):
            with self.assertRaises(ValidationError):
                self.serializer.validate(data)

    def test_validate_creates_model_instance_with_data(self):
        """Test that validate creates model instance with the provided data"""
        data = {"value": 15, "value_b": 25}

        with patch.object(CommonInfoBasedModel, "clean"):
            with patch.object(CommonInfoBasedModel, "__init__", return_value=None) as mock_init:
                self.serializer.validate(data)

                mock_init.assert_called_once_with(**data)


class CommonInfoSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.factory = APIRequestFactory()

    def test_validate_with_authenticated_user_new_instance(self):
        """Test validate adds user fields for new instance with authenticated user"""
        request = self.factory.get("/")
        request.user = self.user

        serializer = DummyCommonInfoSerializer(context={"request": request})
        data = {"value": 10, "value_b": 20}

        with patch.object(CommonInfoBasedModel, "clean"):
            result = serializer.validate(data)

            self.assertEqual(result["lastmodified_by"], self.user)
            self.assertEqual(result["created_by"], self.user)

    def test_validate_with_authenticated_user_existing_instance(self):
        """Test validate adds lastmodified_by but not created_by for existing instance"""
        instance = CommonInfoBasedModel.objects.create(value=5, value_b=10)
        request = self.factory.get("/")
        request.user = self.user

        serializer = DummyCommonInfoSerializer(instance=instance, context={"request": request})
        data = {"value": 15, "value_b": 25}

        with patch.object(CommonInfoBasedModel, "clean"):
            result = serializer.validate(data)

            self.assertEqual(result["lastmodified_by"], self.user)
            self.assertNotIn("created_by", result)

    def test_validate_without_request_in_context(self):
        """Test validate when no request in context"""
        serializer = DummyCommonInfoSerializer(context={})
        data = {"value": 10, "value_b": 20}

        with patch.object(CommonInfoBasedModel, "clean"):
            # This should raise AttributeError due to the bug in the code
            # where it doesn't check if request is None before accessing request.user
            with self.assertRaises(AttributeError):
                serializer.validate(data)

    def test_validate_with_request_but_no_user(self):
        """Test validate when request exists but has no user"""
        request = self.factory.get("/")
        request.user = None

        serializer = DummyCommonInfoSerializer(context={"request": request})
        data = {"value": 10, "value_b": 20}

        with patch.object(CommonInfoBasedModel, "clean"):
            result = serializer.validate(data)

            # Should not add user fields when no user
            self.assertNotIn("lastmodified_by", result)
            self.assertNotIn("created_by", result)

    def test_validate_with_anonymous_user(self):
        """Test validate with AnonymousUser"""
        request = self.factory.get("/")
        request.user = Mock()
        request.user.__bool__ = Mock(return_value=False)  # Simulate AnonymousUser

        serializer = DummyCommonInfoSerializer(context={"request": request})
        data = {"value": 10, "value_b": 20}

        with patch.object(CommonInfoBasedModel, "clean"):
            result = serializer.validate(data)

            # Should not add user fields for anonymous user
            self.assertNotIn("lastmodified_by", result)
            self.assertNotIn("created_by", result)

    def test_validate_calls_super_validate(self):
        """Test that CommonInfoSerializer calls parent validate method"""
        request = self.factory.get("/")
        request.user = self.user

        serializer = DummyCommonInfoSerializer(context={"request": request})
        data = {"value": 10, "value_b": 20}

        with patch.object(BaseModelSerializer, "validate", return_value=data) as mock_super:
            with patch.object(CommonInfoBasedModel, "clean"):
                result = serializer.validate(data)

                mock_super.assert_called_once_with(data)
                # Result should include both original data and user fields
                self.assertIn("value", result)
                self.assertIn("value_b", result)
                self.assertEqual(result["lastmodified_by"], self.user)
                self.assertEqual(result["created_by"], self.user)
