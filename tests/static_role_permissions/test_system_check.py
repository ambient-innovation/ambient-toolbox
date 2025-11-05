from unittest import mock

from django.apps import apps
from django.contrib.auth import get_permission_codename
from django.core.checks import Warning as DjangoWarning
from django.db import models
from django.test import TestCase, override_settings

from ambient_toolbox.static_role_permissions.system_check import (
    check_permissions_against_models,
    collect_model_permissions,
)


class CollectModelPermissionsTest(TestCase):
    """Test suite for collect_model_permissions function."""

    def test_collect_model_permissions_with_default_permissions(self):
        """Test that default permissions are collected correctly."""
        app_configs = [apps.get_app_config("auth")]
        permissions = collect_model_permissions(app_configs)

        # Check that default permissions for User model are present
        self.assertIn("auth.add_user", permissions)
        self.assertIn("auth.change_user", permissions)
        self.assertIn("auth.delete_user", permissions)
        self.assertIn("auth.view_user", permissions)

    def test_collect_model_permissions_with_custom_permissions(self):
        """Test that custom permissions are collected correctly."""

        class SystemCheckTestModel(models.Model):  # noqa: DJ008
            class Meta:
                app_label = "testapp"
                permissions = [
                    ("custom_permission", "Can do custom action"),
                    ("another_custom", "Another custom permission"),
                ]

        # Get the testapp config
        app_configs = [apps.get_app_config("testapp")]
        permissions = collect_model_permissions(app_configs)

        # Check that custom permissions are included
        self.assertIn("testapp.custom_permission", permissions)
        self.assertIn("testapp.another_custom", permissions)

    def test_collect_model_permissions_multiple_apps(self):
        """Test collecting permissions from multiple apps."""
        app_configs = [
            apps.get_app_config("auth"),
            apps.get_app_config("contenttypes"),
        ]
        permissions = collect_model_permissions(app_configs)

        # Check permissions from both apps
        self.assertIn("auth.add_user", permissions)
        self.assertIn("contenttypes.add_contenttype", permissions)

    def test_collect_model_permissions_empty_list(self):
        """Test with empty app_configs list."""
        permissions = collect_model_permissions([])
        self.assertEqual(permissions, set())

    def test_collect_model_permissions_returns_set(self):
        """Test that the function returns a set."""
        app_configs = [apps.get_app_config("auth")]
        permissions = collect_model_permissions(app_configs)
        self.assertIsInstance(permissions, set)

    def test_collect_model_permissions_with_model_without_custom_permissions(self):
        """Test collecting permissions from a model with only default permissions."""
        app_configs = [apps.get_app_config("auth")]
        permissions = collect_model_permissions(app_configs)

        # User model should have default permissions
        opts = apps.get_model("auth", "User")._meta
        for action in opts.default_permissions:
            codename = get_permission_codename(action, opts)
            self.assertIn(f"auth.{codename}", permissions)


class CheckPermissionsAgainstModelsTest(TestCase):
    """Test suite for check_permissions_against_models function."""

    @mock.patch(
        "ambient_toolbox.static_role_permissions.system_check.load_static_role_permissions",
        return_value={
            "admin": {"auth.add_user", "auth.change_user"},
            "viewer": {"auth.view_user"},
        },
    )
    def test_check_permissions_against_models_all_valid(self, _):
        """Test when all permissions exist in models."""
        app_configs = [apps.get_app_config("auth")]
        errors = check_permissions_against_models(app_configs)
        self.assertEqual(errors, [])

    @mock.patch(
        "ambient_toolbox.static_role_permissions.system_check.load_static_role_permissions",
        return_value={
            "admin": {"auth.nonexistent_permission"},
        },
    )
    def test_check_permissions_against_models_invalid_permission(self, _):
        """Test when a permission doesn't exist in models."""
        app_configs = [apps.get_app_config("auth")]
        errors = check_permissions_against_models(app_configs)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], DjangoWarning)
        self.assertEqual(errors[0].msg, "Permission does not exist in any model.")
        self.assertIn("auth.nonexistent_permission", errors[0].obj)
        self.assertIn("admin", errors[0].obj)

    @mock.patch(
        "ambient_toolbox.static_role_permissions.system_check.load_static_role_permissions",
        return_value={
            "admin": {"auth.add_user", "nonexistent.permission", "another.bad_perm"},
        },
    )
    def test_check_permissions_against_models_breaks_on_first_error(self, _):
        """Test that the function breaks after finding the first invalid permission in a role."""
        app_configs = [apps.get_app_config("auth")]
        errors = check_permissions_against_models(app_configs)

        # Should only have one error due to the break statement
        self.assertEqual(len(errors), 1)
        # The error should be one of the invalid permissions (set iteration order is not guaranteed)
        self.assertTrue("nonexistent.permission" in errors[0].obj or "another.bad_perm" in errors[0].obj)

    @mock.patch(
        "ambient_toolbox.static_role_permissions.system_check.load_static_role_permissions",
        return_value={
            "role1": {"auth.add_user"},
            "role2": {"auth.change_user"},
        },
    )
    def test_check_permissions_against_models_multiple_roles_all_valid(self, _):
        """Test with multiple roles, all with valid permissions."""
        app_configs = [apps.get_app_config("auth")]
        errors = check_permissions_against_models(app_configs)
        self.assertEqual(errors, [])

    @mock.patch(
        "ambient_toolbox.static_role_permissions.system_check.load_static_role_permissions",
        return_value={
            "role1": {"auth.add_user"},
            "role2": {"invalid.permission"},
        },
    )
    def test_check_permissions_against_models_second_role_has_error(self, _):
        """Test when the second role has an invalid permission."""
        app_configs = [apps.get_app_config("auth")]
        errors = check_permissions_against_models(app_configs)

        self.assertEqual(len(errors), 1)
        self.assertIn("invalid.permission", errors[0].obj)
        self.assertIn("role2", errors[0].obj)

    @mock.patch("ambient_toolbox.static_role_permissions.system_check.apps.get_app_configs")
    @mock.patch(
        "ambient_toolbox.static_role_permissions.system_check.load_static_role_permissions",
        return_value={"admin": {"auth.add_user"}},
    )
    def test_check_permissions_against_models_none_app_configs(self, _, mock_get_app_configs):
        """Test when app_configs is None (should use all apps)."""
        mock_get_app_configs.return_value = [apps.get_app_config("auth")]

        errors = check_permissions_against_models(app_configs=None)

        mock_get_app_configs.assert_called_once()
        self.assertEqual(errors, [])

    @mock.patch(
        "ambient_toolbox.static_role_permissions.system_check.load_static_role_permissions",
        return_value={},
    )
    def test_check_permissions_against_models_empty_permissions_dict(self, _):
        """Test with empty permissions dictionary."""
        app_configs = [apps.get_app_config("auth")]
        errors = check_permissions_against_models(app_configs)
        self.assertEqual(errors, [])

    @mock.patch(
        "ambient_toolbox.static_role_permissions.system_check.load_static_role_permissions",
        return_value={
            "admin": set(),
        },
    )
    def test_check_permissions_against_models_empty_permission_set(self, _):
        """Test with a role that has an empty permission set."""
        app_configs = [apps.get_app_config("auth")]
        errors = check_permissions_against_models(app_configs)
        self.assertEqual(errors, [])

    @mock.patch(
        "ambient_toolbox.static_role_permissions.system_check.load_static_role_permissions",
        return_value={
            "admin": {"auth.add_user", "auth.view_user"},
            "editor": {"auth.change_user"},
            "viewer": {"auth.delete_user"},
        },
    )
    def test_check_permissions_against_models_multiple_roles_complex(self, _):
        """Test with multiple roles and complex permission sets."""
        app_configs = [apps.get_app_config("auth")]
        errors = check_permissions_against_models(app_configs)
        self.assertEqual(errors, [])

    @override_settings(STATIC_ROLE_PERMISSIONS_PATH="tests.static_role_permissions.dummy_permissions.PERMISSIONS_DICT")
    def test_check_permissions_against_models_integration(self):
        """Integration test with actual permissions from settings."""
        # dummy_permissions.PERMISSIONS_DICT has auth.add_user and auth.view_user which are valid
        app_configs = [apps.get_app_config("auth")]
        errors = check_permissions_against_models(app_configs)
        self.assertEqual(errors, [])
