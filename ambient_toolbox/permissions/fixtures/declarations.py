import dataclasses


@dataclasses.dataclass
class PermissionModelDeclaration:
    app_label: str
    codename_list: list[str]
    model: str


@dataclasses.dataclass
class GroupPermissionDeclaration:
    name: str
    permission_list: list[PermissionModelDeclaration]
