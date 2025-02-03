from django.utils.module_loading import import_string

from ambient_toolbox.static_role_permissions.settings import get_static_role_permissions_path


def load_static_role_permissions() -> dict[str, set[str]]:
    """
    Load static definition of permissions by role.

    Example:
    {
        "role_1": {
            "app_label.permission",
            "app_label.permission",
            ...
        },
        "role_2": {
            "app_label.permission",
            "app_label.permission",
            ...
        },
    """
    dotted_path = get_static_role_permissions_path()
    assert dotted_path, "STATIC_ROLE_PERMISSIONS_PATH is not set in settings.py"

    permission = import_string(dotted_path)
    assert isinstance(permission, dict), "STATIC_ROLE_PERMISSIONS_PATH must point to a dict"

    return permission
