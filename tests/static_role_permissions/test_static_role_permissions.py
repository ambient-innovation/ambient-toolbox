from unittest import mock

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, override_settings

from ambient_toolbox.static_role_permissions.permissions import load_static_role_permissions


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "ambient_toolbox.static_role_permissions.auth_backend.StaticRolePermissionBackend",
    ]
)
class StaticRolePermissionTests(TestCase):
    @override_settings(STATIC_ROLE_PERMISSIONS_PATH="tests.static_role_permissions.dummy_permissions.PERMISSIONS_DICT")
    def test_load_permissions_from_settings_path(self):
        permissions = load_static_role_permissions()
        self.assertEqual(
            {"role_1": {"auth.add_user", "auth.view_user"}, "role_2": {}},
            permissions,
        )

    def test_load_permissions_from_settings_path_without_path_set(self):
        with self.assertRaisesMessage(AssertionError, "STATIC_ROLE_PERMISSIONS_PATH is not set in settings.py"):
            load_static_role_permissions()

    @override_settings(STATIC_ROLE_PERMISSIONS_PATH="tests.static_role_permissions.dummy_permissions.PERMISSIONS_LIST")
    def test_load_permissions_from_settings_path_with_invalid_dict(self):
        with self.assertRaisesMessage(AssertionError, "STATIC_ROLE_PERMISSIONS_PATH must point to a dict"):
            load_static_role_permissions()

    def test_has_perm_without_user_role(self):
        user = User()  # user.role does not exist
        self.assertEqual(False, user.has_perm("auth.add_user"))

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={
            "role_1": {"app_label.permission_1", "app_label.permission_2"},
        },
    )
    def test_has_perm_true_with_role_in_dict(self, _):
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
        user = User()
        user.role = "role_1"
        user.is_active = False
        self.assertEqual(False, user.has_perm("app_label.permission_1"))

    @mock.patch(
        "ambient_toolbox.static_role_permissions.auth_backend.load_static_role_permissions",
        return_value={},
    )
    def test_has_perm_false_for_superuser_without_role(self, _):
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
        anon = AnonymousUser()
        anon.role = "role_1"
        self.assertEqual(False, anon.has_perm("app_label.permission_1"))
