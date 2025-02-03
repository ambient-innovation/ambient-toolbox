from django.test import override_settings

from ambient_toolbox.static_role_permissions.settings import (
    get_static_role_permissions_enable_system_check,
    get_static_role_permissions_path,
)


@override_settings(STATIC_ROLE_PERMISSIONS_PATH="/path/to/permissions")
def test_get_static_role_permissions_path_is_set():
    assert get_static_role_permissions_path() == "/path/to/permissions"


def test_get_static_role_permissions_path_default_used():
    assert get_static_role_permissions_path() is None


@override_settings(STATIC_ROLE_PERMISSIONS_ENABLE_SYSTEM_CHECK=False)
def test_get_static_role_permissions_enable_system_check_is_set():
    assert get_static_role_permissions_enable_system_check() is False


def test_get_static_role_permissions_enable_system_check_default_used():
    assert get_static_role_permissions_enable_system_check() is True
