import os
import sys
import warnings
from pathlib import Path

from django.conf import settings

from ambient_toolbox.tests.structure_validator import settings as toolbox_settings

REMOVAL_NOTE = "will be removed in 13.0.0"


class StructureTestValidator:
    file_allowlist: list
    issue_list: list

    def __init__(self):
        self.file_allowlist = self._call_hook("_get_file_allowlist", legacy_name="_get_file_whitelist")
        self.issue_list = []

    @property
    def file_whitelist(self) -> list:
        warnings.warn(
            f"StructureTestValidator.file_whitelist is deprecated and {REMOVAL_NOTE}, use file_allowlist",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.file_allowlist

    @file_whitelist.setter
    def file_whitelist(self, value: list) -> None:
        warnings.warn(
            f"StructureTestValidator.file_whitelist is deprecated and {REMOVAL_NOTE}, use file_allowlist",
            DeprecationWarning,
            stacklevel=2,
        )
        self.file_allowlist = value

    def _call_hook(self, name: str, *, legacy_name: str) -> list:
        """
        Calls the hook `name`, unless a subclass or mock replaced the deprecated hook `legacy_name`.
        Then the legacy hook is called, so existing customisations keep working.
        """
        if getattr(type(self), legacy_name) is not _ORIGINAL_LEGACY_HOOKS[legacy_name]:
            warnings.warn(
                f"Overriding StructureTestValidator.{legacy_name}() is deprecated and {REMOVAL_NOTE}, "
                f"override {name}() instead",
                DeprecationWarning,
                stacklevel=3,
            )
            return getattr(self, legacy_name)()
        return getattr(self, name)()

    @staticmethod
    def _resolve_allowlist_setting(
        allowlist_name: str,
        whitelist_name: str,
        default: list,
    ) -> list:
        if hasattr(settings, allowlist_name):
            return getattr(settings, allowlist_name)
        if hasattr(settings, whitelist_name):
            warnings.warn(
                f"{whitelist_name} is deprecated and {REMOVAL_NOTE}, use {allowlist_name}",
                FutureWarning,
                stacklevel=3,
            )
            return getattr(settings, whitelist_name)

        if hasattr(toolbox_settings, allowlist_name):
            return getattr(toolbox_settings, allowlist_name)
        if hasattr(toolbox_settings, whitelist_name):
            warnings.warn(
                f"{whitelist_name} is deprecated and {REMOVAL_NOTE}, use {allowlist_name}",
                FutureWarning,
                stacklevel=3,
            )
            return getattr(toolbox_settings, whitelist_name)

        return default

    @staticmethod
    def _get_file_allowlist() -> list:
        default_allowlist = ["__init__"]
        configured = StructureTestValidator._resolve_allowlist_setting(
            allowlist_name="TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST",
            whitelist_name="TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST",
            default=[],
        )
        return default_allowlist + configured

    @staticmethod
    def _get_file_whitelist() -> list:
        warnings.warn(
            f"StructureTestValidator._get_file_whitelist() is deprecated and {REMOVAL_NOTE}, use _get_file_allowlist()",
            DeprecationWarning,
            stacklevel=2,
        )
        return StructureTestValidator._get_file_allowlist()

    @staticmethod
    def _get_base_dir() -> Path | str:
        try:
            return settings.TEST_STRUCTURE_VALIDATOR_BASE_DIR
        except AttributeError:
            return toolbox_settings.TEST_STRUCTURE_VALIDATOR_BASE_DIR

    @staticmethod
    def _get_base_app_name() -> str:
        try:
            return settings.TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME
        except AttributeError:
            return toolbox_settings.TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME

    @staticmethod
    def _get_ignored_directory_list() -> list:
        default_dir_list = ["__pycache__"]
        try:
            return default_dir_list + settings.TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST
        except AttributeError:
            return default_dir_list + toolbox_settings.TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST

    @staticmethod
    def _get_app_list() -> list | tuple:
        try:
            return settings.TEST_STRUCTURE_VALIDATOR_APP_LIST
        except AttributeError:
            return toolbox_settings.TEST_STRUCTURE_VALIDATOR_APP_LIST

    @staticmethod
    def _get_misplaced_test_file_allowlist() -> list:
        return StructureTestValidator._resolve_allowlist_setting(
            allowlist_name="TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_ALLOWLIST",
            whitelist_name="TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST",
            default=[],
        )

    @staticmethod
    def _get_misplaced_test_file_whitelist() -> list:
        warnings.warn(
            f"StructureTestValidator._get_misplaced_test_file_whitelist() is deprecated and {REMOVAL_NOTE}, "
            "use _get_misplaced_test_file_allowlist()",
            DeprecationWarning,
            stacklevel=2,
        )
        return StructureTestValidator._get_misplaced_test_file_allowlist()

    def _check_missing_test_prefix(self, *, root: str, file: str, filename: str, extension: str) -> bool:
        if extension == ".py" and not filename[0:5] == "test_" and filename not in self.file_allowlist:
            file_path = f"{root}\\{file}".replace("\\", "/")
            self.issue_list.append(f'Python file without "test_" prefix found: {file_path!r}.')
            return False
        return True

    def _check_missing_init(self, *, root: str, init_found: bool, number_of_py_files: int) -> bool:
        if not init_found and number_of_py_files > 0:
            path = root.replace("\\", "/")
            self.issue_list.append(f"__init__.py missing in {path!r}.")
            return False
        return True

    def _check_misplaced_test_files(self) -> None:
        """Check for files starting with 'test_' that are not in or under a 'tests/' directory."""
        base_dir = self._get_base_dir()
        allowlist = self._call_hook(
            "_get_misplaced_test_file_allowlist", legacy_name="_get_misplaced_test_file_whitelist"
        )

        for root, dirs, files in os.walk(base_dir):
            # Skip directories in the ignored list
            for excluded_dir in self._get_ignored_directory_list():
                if excluded_dir in dirs:
                    dirs.remove(excluded_dir)

            cleaned_root = root.replace("\\", "/")

            # Check if current path contains 'tests' as a directory component
            path_parts = Path(cleaned_root).parts
            has_tests_parent = any(part == "tests" for part in path_parts)

            if not has_tests_parent:
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        file_path = f"{cleaned_root}/{file}".replace("\\", "/")

                        # Check if the file path matches any allowlist pattern
                        is_allowlisted = any(allowlist_pattern in file_path for allowlist_pattern in allowlist)

                        if not is_allowlisted:
                            self.issue_list.append(f"Test file found outside tests directory: {file_path!r}.")

    def _build_path_to_test_package(self, app: str) -> Path:
        return self._get_base_dir() / Path(app.replace(".", "/")) / "tests"

    def process(self) -> None:  # noqa: C901
        backend_package = self._get_base_app_name()
        app_list = self._get_app_list()

        # Check for misplaced test files first
        self._check_misplaced_test_files()

        for app in app_list:
            if not app.startswith(backend_package):
                continue
            app_path = self._build_path_to_test_package(app=app)
            for root, dirs, files in os.walk(app_path):
                cleaned_root = root.replace("\\", "/")
                print(f"Inspecting {cleaned_root!r}...")
                init_found = False
                number_of_py_files = 0

                for excluded_dir in self._get_ignored_directory_list():
                    try:
                        dirs.remove(excluded_dir)
                    except ValueError:
                        pass

                for file in files:
                    filename = file[:-3]
                    extension = file[-3:]

                    if filename == "__init__":
                        init_found = True

                    if extension == ".py":
                        number_of_py_files += 1

                    # Check for missing test prefix
                    self._check_missing_test_prefix(root=root, file=file, filename=filename, extension=extension)

                # Check for missing init file
                self._check_missing_init(root=root, init_found=init_found, number_of_py_files=number_of_py_files)

        number_of_issues = len(self.issue_list)

        if number_of_issues:
            print("=======================")
            print("Errors found:")

            for issue in self.issue_list:
                print(f"- {issue}")

        print("=======================")

        if number_of_issues:
            print(f"Checking test structure failed with {number_of_issues} issue(s).")
            sys.exit(1)
        else:
            print("0 issues detected. Yeah!")


# Captured at import time to detect subclasses or mocks replacing a deprecated hook
_ORIGINAL_LEGACY_HOOKS = {
    name: getattr(StructureTestValidator, name)
    for name in ("_get_file_whitelist", "_get_misplaced_test_file_whitelist")
}
