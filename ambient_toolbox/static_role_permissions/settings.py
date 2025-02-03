from typing import Optional

from django.conf import settings


def get_static_role_permissions_path() -> Optional[str]:
    """
    Path where role permissions are defined at.
    """
    return getattr(settings, "STATIC_ROLE_PERMISSIONS_PATH", None)


def get_static_role_permissions_enable_system_check() -> bool:
    """
    Switch to enable system checks for the role permission feature.
    """
    return getattr(settings, "STATIC_ROLE_PERMISSIONS_ENABLE_SYSTEM_CHECK", True)
