# Permissions

## Improved group permission fixtures

### Motivation

Many applications require a deterministic assignment of Django groups and permissions. To ensure this, many developers
rely on Django JSON fixtures which are installed during deployment.

Django fixtures are a simple way of ensuring that certain records are cemented within the database. It works reliable
but has some drawbacks:

1. The ID is exported as well. This can cause problems on different systems.
2. The JSON structure is hard to manipulate manually and prone to merge conflicts.
3. Exporting exactly what you need without getting stuff you don't want to have might be challenging.

Therefore, we implemented a nice, 100% Python way of ensuring your group permissions are the way you want them.

1. No JSON, only Python dataclasses (explicit is better than implicit)
2. Everything is under version control
3. Separation possibility per app for the permissions reduces the change of having merge conflicts

### Getting started

Create a new python package called `permissions` within your applications "auth" or "account" django app. If you don't
have any, create one. Next, create a Python file with the same name as your group, let's say "editor".

````python
# account/permissions/editor.py

import dataclasses
from ambient_toolbox.permissions.fixtures.declarations import GroupPermissionDeclaration, PermissionModelDeclaration


@dataclasses.dataclass
class GroupEditor(GroupPermissionDeclaration):
    name = 'editor'
    permission_list = [
        PermissionModelDeclaration(
            app_label='content_management',
            codename_list=[
                'add_article',
                'change_article',
                'view_article',
            ],
            model='article',
        ),
    ]
````

You create an instance of `GroupPermissionDeclaration` for every group. Then you can add as many
`PermissionModelDeclaration` as you like.

The permission declaration is per model to save you some characters and to reduce the size of the file.

When you've declared all your groups as described, you have to register them within your Django settings.

````python
# Improved fixtures (provided by "ambient-toolbox")
GROUP_PERMISSION_FIXTURES = (
    'account.permissions.editor.GroupEditor',
    ...
)
````

### Separating your apps

Having a huge file per group integrating model permissions from all over your application will increase the coupling
your django apps have. Therefore, we recommend, that you create one permission file per group per django app which you
then import in your group declaration.

Permission declaration

````python
# content_management/permissions/groups/editor.py

from ambient_toolbox.permissions.fixtures.declarations import PermissionModelDeclaration

CONTENT_MANAGEMENT_PERMISSIONS = [
    PermissionModelDeclaration(
        app_label='content_management',
        codename_list=[
            'add_article',
            'change_article',
            'view_article',
        ],
        model='article',
    ),
    PermissionModelDeclaration(
        app_label='content_management',
        codename_list=[
            'add_employee',
            'change_employee',
            'delete_image'
            'view_employee',
        ],
        model='image',
    ),
]
````

Group declaration:

````python
# account/permissions/editor.py

import dataclasses

from ambient_toolbox.permissions.fixtures.declarations import GroupPermissionDeclaration
from content_management.permissions.groups.editor import CONTENT_MANAGEMENT_PERMISSIONS


@dataclasses.dataclass
class GroupEditor(GroupPermissionDeclaration):
    name = 'editor'
    permission_list = [
        *CONTENT_MANAGEMENT_PERMISSIONS,
    ]
````

### Convenience helpers

Often, you'll assign all four default permissions (add, change, delete and view). To keep you from writing too many
code, you can use this helper which will return all default permission strings.

Surely, you can add more custom permissions after using this helper.

````python
# account/permissions/editor.py

import dataclasses
from ambient_toolbox.permissions.fixtures.declarations import GroupPermissionDeclaration, PermissionModelDeclaration
from ambient_toolbox.permissions.fixtures.helpers import generate_default_permissions


@dataclasses.dataclass
class GroupEditor(GroupPermissionDeclaration):
    name = 'editor'
    permission_list = [
        PermissionModelDeclaration(
            app_label='content_management',
            codename_list=[
                *generate_default_permissions('article'),
                'my_custom_permission_for_article',
            ],
            model='article',
        ),
    ]
````

This way your group files won't contain an insane amount of LOC and your apps are at least only loosely coupled.

### Installing your fixtures

To install your fixtures after the deployment, call this convenient management command.

> python ./manage.py install_permission_fixtures

Note, that this command will check your permissions. If it finds an invalid permission, it will raise a meaningful
exception.

### Validation / pipeline check

If you want to validate that you didn't make any mistakes, you can run the same command as a "dry-run" in your CI/CD.

> python ./manage.py install_permission_fixtures --dry-run

### Testing

To ensure that your setup is correct, and you use only valid and existing permissions, you can write a quick integration
test. Note that removing a Django permission code-wise won't result in removing it in the database. So having a
non-existing permission in your permission fixtures might not necessarily lead to an error. The test database on the
other hand is created from scratch and therefore only contains valid permissions.

````python
from django.core.management import call_command
from django.test import TestCase


class PermissionFixturesIntegrationTest(TestCase):

    def test_integration_regular(self):
        call_command('install_permission_fixtures', '--dry-run')
````

### Limitations

Please note that new groups will be created but the service won't **delete** any groups. The simple reason is that if
you rename a group, this would count as a "delete" and a "create" operation. The new group would have all permissions,
but all user assignments would be lost on deleting the previous group.
