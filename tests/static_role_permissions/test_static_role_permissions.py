from unittest import mock

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, override_settings

from ambient_toolbox.static_role_permissions.auth_backend import StaticRolePermissionBackend
from ambient_toolbox.static_role_permissions.permissions import load_static_role_permissions


class LoadStaticRolePermissionsTest(TestCase):
    """Test suite for load_static_role_permissions function."""

    @override_settings(STATIC_ROLE_PERMISSIONS_PATH="tests.static_role_permissions.dummy_permissions.PERMISSIONS_DICT")
    def test_load_permissions_from_settings_path(self):
        """Test loading permissions from a valid settings path."""
        permissions = load_static_role_permissions()
        self.assertEqual(
            {"role_1": {"auth.add_user", "auth.view_user"}, "role_2": {}},
            permissions,
        )

    def test_load_permissions_from_settings_path_without_path_set(self):
        """Test that an error is raised when STATIC_ROLE_PERMISSIONS_PATH is not set."""
        with self.assertRaisesMessage(AssertionError, "STATIC_ROLE_PERMISSIONS_PATH is not set in settings.py"):
            load_static_role_permissions()

    @override_settings(STATIC_ROLE_PERMISSIONS_PATH="tests.static_role_permissions.dummy_permissions.PERMISSIONS_LIST")
    def test_load_permissions_from_settings_path_with_invalid_dict(self):
        """Test that an error is raised when the path points to a non-dict."""
        with self.assertRaisesMessage(AssertionError, "STATIC_ROLE_PERMISSIONS_PATH must point to a dict"):
            load_static_role_permissions()


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "ambient_toolbox.static_role_permissions.auth_backend.StaticRolePermissionBackend",
    ]
)
class StaticRolePermissionBackendTest(TestCase):
    """Test suite for StaticRolePermissionBackend."""

    def test_init_sets_cache_to_none(self):
        """Test that __init__ sets _static_permissions_cache to None."""
        backend = StaticRolePermissionBackend()
        self.assertIsNone(backend._static_permissions_cache)

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={"role_1": {"perm1"}},
    )
    def test_get_static_role_permissions_caches_result(self, mock_load):
        """Test that _get_static_role_permissions caches the result."""
        backend = StaticRolePermissionBackend()

        # First call should load permissions
        result1 = backend._get_static_role_permissions()
        self.assertEqual(result1, {"role_1": {"perm1"}})
        self.assertEqual(mock_load.call_count, 1)

        # Second call should use cache
        result2 = backend._get_static_role_permissions()
        self.assertEqual(result2, {"role_1": {"perm1"}})
        self.assertEqual(mock_load.call_count, 1)  # Still 1, not called again

        # Verify cache is set
        self.assertIsNotNone(backend._static_permissions_cache)

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={
            "role_1": {"app_label.permission_1", "app_label.permission_2"},
            "role_2": {"app_label.permission_3"},
        },
    )
    def test_get_permissions_for_role_existing_role(self, _):
        """Test getting permissions for an existing role."""
        backend = StaticRolePermissionBackend()
        permissions = backend._get_permissions_for_role("role_1")
        self.assertEqual(permissions, {"app_label.permission_1", "app_label.permission_2"})

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={"role_1": {"perm1"}},
    )
    def test_get_permissions_for_role_missing_role(self, _):
        """Test getting permissions for a non-existent role returns empty set."""
        backend = StaticRolePermissionBackend()
        permissions = backend._get_permissions_for_role("role_999")
        self.assertEqual(permissions, set())

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={"role_1": {"app_label.permission_1"}},
    )
    def test_get_all_permissions_with_obj_returns_empty(self, _):
        """Test that get_all_permissions returns empty set when obj is provided."""
        backend = StaticRolePermissionBackend()
        user = User()
        user.role = "role_1"
        user.is_active = True

        permissions = backend.get_all_permissions(user, obj=object())
        self.assertEqual(permissions, set())

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={"role_1": {"app_label.permission_1"}},
    )
    def test_get_all_permissions_inactive_user(self, _):
        """Test that inactive users get no permissions."""
        backend = StaticRolePermissionBackend()
        user = User()
        user.role = "role_1"
        user.is_active = False

        permissions = backend.get_all_permissions(user)
        self.assertEqual(permissions, set())

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={"role_1": {"app_label.permission_1"}},
    )
    def test_get_all_permissions_anonymous_user(self, _):
        """Test that anonymous users get no permissions."""
        backend = StaticRolePermissionBackend()
        anon = AnonymousUser()
        anon.role = "role_1"

        permissions = backend.get_all_permissions(anon)
        self.assertEqual(permissions, set())

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={"role_1": {"app_label.permission_1"}},
    )
    def test_get_all_permissions_user_without_role(self, _):
        """Test that users without a role attribute get no permissions."""
        backend = StaticRolePermissionBackend()
        user = User()
        user.is_active = True

        permissions = backend.get_all_permissions(user)
        self.assertEqual(permissions, set())

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={"role_1": {"app_label.permission_1", "app_label.permission_2"}},
    )
    def test_get_all_permissions_valid_user(self, _):
        """Test that valid users with roles get their permissions."""
        backend = StaticRolePermissionBackend()
        user = User()
        user.role = "role_1"
        user.is_active = True

        permissions = backend.get_all_permissions(user)
        self.assertEqual(permissions, {"app_label.permission_1", "app_label.permission_2"})


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "ambient_toolbox.static_role_permissions.auth_backend.StaticRolePermissionBackend",
    ]
)
class StaticRolePermissionIntegrationTest(TestCase):
    """Integration tests for StaticRolePermissionBackend with Django's permission system."""

    def test_has_perm_without_user_role(self):
        """Test that users without a role attribute have no permissions."""
        user = User()  # user.role does not exist
        self.assertEqual(False, user.has_perm("auth.add_user"))

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={
            "role_1": {"app_label.permission_1", "app_label.permission_2"},
        },
    )
    def test_has_perm_true_with_role_in_dict(self, _):
        """Test that has_perm returns True for permissions in user's role."""
        user = User()
        user.role = "role_1"
        self.assertEqual(True, user.has_perm("app_label.permission_1"))

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={
            "role_1": {"app_label.permission_1", "app_label.permission_2"},
        },
    )
    def test_has_perm_false_with_perm_not_in_set(self, _):
        """Test that has_perm returns False for permissions not in user's role."""
        user = User()
        user.role = "role_1"
        self.assertEqual(False, user.has_perm("app_label.permission_3"))

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={
            "role_1": {},
        },
    )
    def test_has_perm_false_with_empty_set(self, _):
        """Test that has_perm returns False when role has empty permission set."""
        user = User()
        user.role = "role_1"
        self.assertEqual(False, user.has_perm("app_label.permission_1"))

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={
            "role_2": {"app_label.permission_1"},  # <-- role_1 is missing
        },
    )
    def test_has_perm_false_with_role_not_in_dict(self, _):
        """Test that has_perm returns False when user's role is not in permissions dict."""
        user = User()
        user.role = "role_1"
        self.assertEqual(False, user.has_perm("app_label.permission_1"))

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={
            "role_1": {"app_label.permission_1"},
        },
    )
    def test_has_perm_false_for_non_active_user(self, _):
        """Test that inactive users have no permissions."""
        user = User()
        user.role = "role_1"
        user.is_active = False
        self.assertEqual(False, user.has_perm("app_label.permission_1"))

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={},
    )
    def test_has_perm_true_for_superuser_without_role(self, _):
        """Test that superusers have all permissions regardless of role."""
        user = User()
        user.is_superuser = True
        self.assertEqual(True, user.has_perm("foo"))

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={
            "role_1": {"app_label.permission_1"},
        },
    )
    def test_has_perm_false_for_anonymous_user(self, _):
        """Test that anonymous users have no permissions."""
        anon = AnonymousUser()
        anon.role = "role_1"
        self.assertEqual(False, anon.has_perm("app_label.permission_1"))
