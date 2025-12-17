from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from ambient_toolbox.models import CommonInfo
from testapp.models import CommonInfoBasedModel


class CreatedAtInfoTest(TestCase):
    """Test suite for CreatedAtInfo model."""

    @freeze_time("2023-01-15 12:30:45")
    def test_created_at_set_on_creation(self):
        """Test that created_at is automatically set on object creation."""
        # Use CommonInfoBasedModel which inherits from CreatedAtInfo
        obj = CommonInfoBasedModel.objects.create(value=1, value_b=1)
        self.assertEqual(obj.created_at, timezone.now())

    @freeze_time("2023-01-15 12:30:45")
    def test_created_at_fallback_when_none(self):
        """Test that save() sets created_at if it's None (fallback for old data)."""
        obj = CommonInfoBasedModel.objects.create(value=1, value_b=1)
        # Simulate old data where created_at might be None
        obj.created_at = None
        obj.save()

        self.assertEqual(obj.created_at, timezone.now())

    def test_created_at_not_overwritten_if_set(self):
        """Test that created_at is not overwritten if already set."""
        original_time = timezone.now() - timezone.timedelta(days=5)
        obj = CommonInfoBasedModel(value=1, value_b=1)
        obj.created_at = original_time
        obj.save()

        self.assertEqual(obj.created_at, original_time)

    def test_save_with_kwargs(self):
        """Test that save() properly passes kwargs to parent."""
        obj = CommonInfoBasedModel(value=1, value_b=1)
        obj.save(force_insert=True)
        self.assertIsNotNone(obj.created_at)


class CommonInfoTest(TestCase):
    """Test suite for CommonInfo model."""

    @freeze_time("2022-06-26 10:00")
    def test_save_created_at_set(self):
        """Test that created_at fallback works (for old data without created_at)."""
        obj = CommonInfoBasedModel.objects.create(value=1, value_b=1)
        obj.created_at = None
        obj.save()

        self.assertEqual(obj.created_at, timezone.now())

    @freeze_time("2022-06-26 10:00")
    def test_save_update_fields_common_fields_set(self):
        """Test that ALWAYS_UPDATE_FIELDS adds common fields to update_fields."""
        with freeze_time("2020-09-19"):
            obj = CommonInfoBasedModel.objects.create(value=1, value_b=1)
        obj.value = 2
        obj.value_b = 999

        # Django's Model.save() can be called with positional args, so we should support this as well.
        args = (
            False,  # default for force_insert
            False,  # default for force_update
            None,  # default for using
            (x for x in ["value"]),  # update_fields is supposed to accept any Iterable[str]
        )
        obj.save(*args)

        obj.refresh_from_db()
        self.assertEqual(obj.value, 2)
        self.assertEqual(obj.value_b, 1, "value_b should not have changed")
        self.assertEqual(obj.lastmodified_at.year, 2022)
        self.assertEqual(obj.lastmodified_at.month, 6)
        self.assertEqual(obj.lastmodified_at.day, 26)
        self.assertEqual(obj.lastmodified_at.hour, 10)

    @patch("testapp.models.CommonInfoBasedModel.ALWAYS_UPDATE_FIELDS", new_callable=PropertyMock)
    @freeze_time("2022-06-26 10:00")
    def test_save_update_fields_common_fields_set_without_always_update(self, always_update_mock):
        """Test that when ALWAYS_UPDATE_FIELDS is False, only specified fields are updated."""
        always_update_mock.return_value = False
        with freeze_time("2020-09-19"):
            obj = CommonInfoBasedModel.objects.create(value=1)
        obj.value = 2
        obj.save(update_fields=("value",))

        obj.refresh_from_db()
        self.assertEqual(obj.value, 2)
        self.assertEqual(obj.lastmodified_at.year, 2020)
        self.assertEqual(obj.lastmodified_at.month, 9)
        self.assertEqual(obj.lastmodified_at.day, 19)
        self.assertEqual(obj.lastmodified_at.hour, 0)

    @freeze_time("2022-06-26 10:00")
    def test_save_common_fields_set_without_update_fields(self):
        """Test that lastmodified_at is always updated on save."""
        with freeze_time("2020-09-19"):
            obj = CommonInfoBasedModel.objects.create(value=1)
        obj.value = 2
        obj.save()

        obj.refresh_from_db()
        self.assertEqual(obj.value, 2)
        self.assertEqual(obj.lastmodified_at.year, 2022)
        self.assertEqual(obj.lastmodified_at.month, 6)
        self.assertEqual(obj.lastmodified_at.day, 26)
        self.assertEqual(obj.lastmodified_at.hour, 10)

    def test_save_common_info_set_user_fields_user_without_pk(self):
        """Test that user fields are not set when user has no pk."""
        obj = CommonInfoBasedModel.objects.create(value=1, value_b=1)
        obj.set_user_fields(user=User(username="username"))

        self.assertIsNone(obj.created_by)
        self.assertIsNone(obj.lastmodified_by)

    def test_save_common_info_set_user_fields_none_user(self):
        """Test that user fields are not set when user is None."""
        obj = CommonInfoBasedModel.objects.create(value=1, value_b=1)
        obj.set_user_fields(user=None)

        self.assertIsNone(obj.created_by)
        self.assertIsNone(obj.lastmodified_by)

    def test_save_common_info_set_user_fields_none_user_no_pk(self):
        """Test set_user_fields with None user on unsaved object."""
        obj = CommonInfoBasedModel(value=1, value_b=1)
        obj.set_user_fields(user=None)

        self.assertIsNone(obj.created_by)
        self.assertIsNone(obj.lastmodified_by)

    def test_save_common_info_set_user_fields_with_valid_user_new_object(self):
        """Test that created_by is set when user has pk and object is new."""
        user = User.objects.create(username="testuser")
        obj = CommonInfoBasedModel(value=1, value_b=1)
        obj.set_user_fields(user=user)

        self.assertEqual(obj.created_by, user)
        self.assertEqual(obj.lastmodified_by, user)

    def test_save_common_info_set_user_fields_with_valid_user_existing_object(self):
        """Test that only lastmodified_by is updated on existing objects."""
        user1 = User.objects.create(username="user1")
        user2 = User.objects.create(username="user2")

        obj = CommonInfoBasedModel.objects.create(value=1, value_b=1)
        obj.created_by = user1
        obj.save()

        # Now modify with a different user
        obj.set_user_fields(user=user2)

        self.assertEqual(obj.created_by, user1, "created_by should not change")
        self.assertEqual(obj.lastmodified_by, user2, "lastmodified_by should update")

    @patch("ambient_toolbox.middleware.current_request.CurrentRequestMiddleware.get_current_user")
    def test_get_current_user_from_middleware(self, mock_get_user):
        """Test that get_current_user calls the middleware."""
        mock_user = User(username="middleware_user")
        mock_get_user.return_value = mock_user

        user = CommonInfo.get_current_user()

        self.assertEqual(user, mock_user)
        mock_get_user.assert_called_once()

    @freeze_time("2022-06-26 10:00")
    def test_save_updates_lastmodified_at(self):
        """Test that lastmodified_at is updated on every save."""
        with freeze_time("2020-01-01"):
            obj = CommonInfoBasedModel.objects.create(value=1)

        obj.value = 2
        obj.save()

        self.assertEqual(obj.lastmodified_at, timezone.now())

    @patch("ambient_toolbox.middleware.current_request.CurrentRequestMiddleware.get_current_user")
    @freeze_time("2022-06-26 10:00")
    def test_save_calls_set_user_fields(self, mock_get_user):
        """Test that save() calls set_user_fields with current user."""
        mock_user = User.objects.create(username="current_user")
        mock_get_user.return_value = mock_user

        obj = CommonInfoBasedModel(value=1, value_b=1)
        obj.save()

        self.assertEqual(obj.created_by, mock_user)
        self.assertEqual(obj.lastmodified_by, mock_user)
