import dataclasses
from typing import List


@dataclasses.dataclass
class PermissionModelDeclaration:
    app_label: str
    codename_list: List[str]
    model: str


@dataclasses.dataclass
class GroupPermissionDeclaration:
    name: str
    permission_list: List[PermissionModelDeclaration]
