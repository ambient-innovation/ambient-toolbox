from ambient_toolbox.permissions.fixtures.declarations import GroupPermissionDeclaration, PermissionModelDeclaration


class TestGroupDeclaration(GroupPermissionDeclaration):
    name = ("group_1",)
    permission_list = [
        PermissionModelDeclaration(
            app_label="testapp",
            codename_list=["view_mysinglesignalmodel"],
            model="mysinglesignalmodel",
        ),
    ]
