import os
import sys
from pathlib import Path
from typing import Union

from django.conf import settings

from ambient_toolbox.tests.structure_validator import settings as toolbox_settings


class TestStructureValidator:
    file_whitelist: list
    issue_list: list

    def __init__(self):
        self.file_whitelist = self._get_file_whitelist()
        self.issue_list = []

    @staticmethod
    def _get_file_whitelist() -> list:
        default_whitelist = ["__init__"]
        try:
            return default_whitelist + settings.TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST
        except AttributeError:
            return default_whitelist + toolbox_settings.TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST

    @staticmethod
    def _get_base_dir() -> Union[Path, str]:
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
    def _get_app_list() -> Union[list, tuple]:
        try:
            return settings.TEST_STRUCTURE_VALIDATOR_APP_LIST
        except AttributeError:
            return toolbox_settings.TEST_STRUCTURE_VALIDATOR_APP_LIST

    def _check_missing_test_prefix(self, *, root: str, file: str, filename: str, extension: str) -> bool:
        if extension == ".py" and not filename[0:5] == "test_" and filename not in self.file_whitelist:
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

    def _build_path_to_test_package(self, app: str) -> Path:
        return self._get_base_dir() / Path(app.replace(".", "/")) / "tests"

    def process(self) -> None:
        backend_package = self._get_base_app_name()
        app_list = self._get_app_list()

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
