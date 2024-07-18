from django.contrib.auth.backends import ModelBackend

from ambient_toolbox.static_role_permissions.permissions import load_static_role_permissions


class StaticRolePermissionBackend(ModelBackend):
    """
    This ModelBackend relies on a static definition of permissions,
    instead of pulling them from the database.

    It expects the user model to have a `role` attribute,
    wich matches with the keys in the STATIC_ROLE_PERMISSIONS dict.

    Example:

    STATIC_ROLE_PERMISSIONS = {
        "admin": {
            "auth.add_user",
            "auth.change_user",
            "auth.delete_user",
        },
        "editor": {
            "auth.add_user",
            "auth.change_user",
        },
        "viewer": {
            "auth.view_user",
        },
    }

    user.role = "admin"

    user.has_perm("auth.add_user") -> True
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._static_permissions_cache = None

    def _get_static_role_permissions(self):
        if self._static_permissions_cache is None:
            self._static_permissions_cache = load_static_role_permissions()
        return self._static_permissions_cache

    def _get_permissions_for_role(self, role: str) -> set[str]:
        role_permissions_dict = self._get_static_role_permissions()
        return role_permissions_dict.get(role, set())

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        role = getattr(user_obj, "role", None)

        if role is None:
            return set()

        return self._get_permissions_for_role(role)
