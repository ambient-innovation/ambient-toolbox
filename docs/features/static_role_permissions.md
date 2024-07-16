# Static Role Permissions

This library provides a highly simplified permission system
based on a static (hardcoded) definition of roles and permissions.

- This saves performance, because it does not require any database queries to check permissions.
- This saves complexity, because the permissions are defined in a simple dictionary. No n:m relations, no changes at runtime.

## Installation

1. Add `StaticRolePermissionBackend` to your `AUTHENTICATION_BACKENDS` in the `settings.py`:

```py
AUTHENTICATION_BACKENDS = [
    # ... other backends
    # 'django.contrib.auth.backends.ModelBackend',  <-- replace the default ModelBackend
    "ambient_toolbox.static_role_permissions.auth_backend.StaticRolePermissionBackend",
]
```

2. Set `STATIC_ROLE_PERMISSIONS_PATH` as dotted path, pointing to a dictionary,
   which defines your permissions per role.

Example:

`settings.py`
```py
STATIC_ROLE_PERMISSIONS_PATH = "my_project.conf.permisions.PERMISSIONS_DICT"
```

`my_project.conf.permisions.py`
```py
PERMISSIONS_DICT: dict[str, set[str]] = {
    "role_1": {"my_app.permission_1", "my_app.permission_2", ...},
    "role_2": {...},
}
```

The roles (keys) and permissions (values) are simple strings.
By default, a system check will match the values against the Django model permission (e.g. `polls.view_poll`)
(see [System check](#system-check) for more information).

In theory, roles and permissions could be any hashable value. Just make sure that the return value of `User.role`
matches the keys of the dictionary.

3. add `ambient_toolbox` to your `INSTALLED_APPS` in the `settings.py` if not already done:

```py
INSTALLED_APPS = [
    # ... other apps
    "ambient_toolbox",
]
```

This is needed to register the [system check](#system-check).

## Simple example

```py
PERMISSIONS_DICT: dict[str, set[str]] = {
    "admin": {
        "auth.view_user",
        "auth.edit_user",
    },
    "customer": {
        "auth.view_user",
    },
}


class User(AbstractUser):
    @property
    def role(self) -> str:
        return "admin" if self.is_staff else "customer"


User(is_staff=True).has_perm("auth.edit_user")  # --> True (without any db query)
```

## Example with role field

This library does not require a role field on the user model, but here is an example how you could implement it:

```py
class UserRoleChoices(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    EMPLOYEE = "EMPLOYEE", "Employee"
    USER = "USER", "User"


class User(AbstractUser):
    role = models.CharField(
        max_length=100,
        choices=UserRoleChoices.choices,
        default=UserRoleChoices.USER,
    )


PERMISSIONS_DICT: dict[str, set[str]] = {
    UserRoleChoices.ADMIN: {...},
    UserRoleChoices.EMPLOYEE: {...},
    UserRoleChoices.USER: {...},
}
```

## System check

By default, this library will register a system check if `STATIC_ROLE_PERMISSIONS_PATH` is set.
The check will go through all the defined permissions and compare them with the Django model permissions.
If any permission does not exist in the Django permission system, a warning will be raised.

This is useful to ensure compatibility with the Django ecosystem and to avoid typos in the permissions.

The system check can be disabled by setting `STATIC_ROLE_PERMISSIONS_DISABLE_SYSTEM_CHECK` to `True` in the settings.

## Why use this library?

Django comes by default with a quite sophisticated permission system.
It is very flexible and covers a lot of use cases for user-based permissions.

Django permission system in a nutshell:
- User have permissions (n:m)
- Users have groups (n:m)
- Groups have permissions (n:m)
- So a user has all permissions of his groups and his own permissions combined
- Permissions are strings like `app_label.permission_name` (e.g. `polls.view_poll`)
- Groups, Permissions and their relations are stored in the db and can be managed via the admin interface at runtime

However, in many cases this adds of lot of complexity to the application, which is not needed.

- When users should only have one group at a time, you still need to manage an n:m relation
- When permissions should not change at runtime, you still need to create and query the permissions via your database.
- When your authorisation logic is not based on permissions at all, you probably still need to deal with permission,
  e.g. in Django Admin, because the Django ecosystem is build around this system.

This library provides a much simpler way to manage permissions, which is based roles and a hardcoded
set of permissions per role.

## Limitations

This library comes with a simple approach for roles / permissions.
If your reality is more complex than that, you should not use it.

E.g when:

- User should have more than one role at a time
- Permissions should be managed at runtime
- You need to assign permissions to individual users
