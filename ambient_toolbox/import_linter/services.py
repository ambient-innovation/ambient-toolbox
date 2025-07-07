from pathlib import Path

import tomlkit
from tomlkit.exceptions import ParseError

from ambient_toolbox.import_linter.projections import ImportLinterContract
from ambient_toolbox.import_linter.settings import (
    get_import_linter_blocklisted_apps,
    get_import_linter_business_logic_apps,
    get_import_linter_local_apps,
    get_import_linter_path_to_toml,
    get_import_linter_root_packages,
)


class ImportLinterContractService:
    def __init__(self):
        super().__init__()

        self.root_packages: list[str] = get_import_linter_root_packages()
        self.business_logic_apps: list[str] = get_import_linter_business_logic_apps()
        self.blocklisted_apps: list[str] = get_import_linter_blocklisted_apps()
        self.local_django_apps: list[str] = get_import_linter_local_apps()
        self.path_to_toml: Path = get_import_linter_path_to_toml()

    def _load_toml_from_pyproject_file(self) -> dict:
        if not self.path_to_toml.exists():
            raise RuntimeError(f"The TOML file {self.path_to_toml} does not exist.")

        with open(self.path_to_toml, "rb") as f:
            try:
                toml_data: dict = tomlkit.load(f)
            except ParseError as e:
                raise RuntimeError(f"The TOML file {self.path_to_toml} is invalid.") from e

        return toml_data

    def _write_to_pyproject_file(self, *, data: dict) -> None:
        rendered_toml = tomlkit.dumps(data)

        with open(self.path_to_toml, "wb") as f:
            f.write(rendered_toml.encode("utf-8"))

    def _create_contracts(self, *, data: dict) -> dict:
        # General import-linter settings
        data.setdefault("tool", {}).setdefault("importlinter", {})
        data["tool"]["importlinter"]["root_packages"] = [
            app for app in self.root_packages if app not in self.blocklisted_apps
        ]
        data["tool"]["importlinter"]["include_external_packages"] = True

        non_managed_contracts = [
            contract
            for contract in data["tool"]["importlinter"]["contracts"]
            if not contract["name"].startswith("[GENERATED]")
        ]

        contracts = []
        for app in [app for app in self.local_django_apps if app not in self.blocklisted_apps]:
            if app in self.business_logic_apps:
                continue
            forbidden = [a for a in self.local_django_apps if a != app and a not in self.blocklisted_apps]
            contracts.append(ImportLinterContract.generate_contract(app=app, forbidden_modules=forbidden).to_dict())

        data["tool"]["importlinter"]["contracts"] = non_managed_contracts + contracts

        return data

    def update_contracts(self):
        toml_data = self._load_toml_from_pyproject_file()

        toml_data = self._create_contracts(data=toml_data)

        self._write_to_pyproject_file(data=toml_data)

    def validate_contracts(self) -> bool:
        current_toml_data = self._load_toml_from_pyproject_file()

        target_toml_data = self._create_contracts(data=current_toml_data)

        return current_toml_data == target_toml_data

    # TODO: tests
    # TODO: docs
