import warnings
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings

from ambient_toolbox.tests.structure_validator import settings as toolbox_settings
from ambient_toolbox.tests.structure_validator.test_structure_validator import StructureTestValidator

# TODO CT: Was this moved?


class TestStructureValidatorTest(TestCase):
    # --------------------- deprecated methods START

    def test_accessing_test_structure_validator_file_whitelist_setting_warns_and_returns_whitelist_value(self):
        toolbox_settings._TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST = "some_allowlist"
        with (
            mock.patch.object(warnings, "warn") as mocked_warn,
        ):
            returned_settings = toolbox_settings.TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST

        mocked_warn.assert_called_once_with(
            "The 'TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST' setting is deprecated and will be removed in"
            "a future version. Use 'TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST' instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )

        self.assertEqual(returned_settings, "some_allowlist")

    def test_setting_test_structure_validator_file_whitelist_setting_warns_and_sets_whitelist_value(self):
        with (
            mock.patch.object(warnings, "warn") as mocked_warn,
        ):
            toolbox_settings.TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST = "some_allowlist"

        mocked_warn.assert_called_once_with(
            "The 'TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST' setting is deprecated and will be removed in "
            "a future version. Use 'TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST' instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )

        self.assertEqual(toolbox_settings._TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST, "some_allowlist")

    @override_settings(TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST=["my_file"])
    def test_accessing_file_whitelist_property_warns_and_returns__file_whitelist(self):
        instance = StructureTestValidator()
        with (
            mock.patch.object(warnings, "warn") as mocked_warn,
        ):
            returned_allowlist = instance.file_whitelist

        mocked_warn.assert_called_once_with(
            "The 'file_whitelist' attribute is deprecated and will be removed in a future version."
            "Use 'file_allowlist' instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )

        self.assertEqual(returned_allowlist, ["__init__", "my_file"])

    @override_settings(TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST=["my_file"])
    def test_setting_file_whitelist_property_warns_and_sets__file_whitelist(self):
        validator_instance = StructureTestValidator()
        with (
            mock.patch.object(warnings, "warn") as mocked_warn,
        ):
            validator_instance.file_whitelist = ["some_file"]

        mocked_warn.assert_called_once_with(
            "The 'file_whitelist' attribute is deprecated and will be removed in a future version."
            "Use 'file_allowlist' instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )

        self.assertEqual(validator_instance._file_whitelist, ["some_file"])

    def test_get_file_whitelist_warns_and_calls_get_file_allowlist(self):
        instance = StructureTestValidator()
        with (
            mock.patch.object(warnings, "warn") as mocked_warn,
            mock.patch.object(StructureTestValidator, "_get_file_allowlist") as mocked_get_file_allowlist,
        ):
            instance._get_file_whitelist()

        mocked_warn.assert_called_once_with(
            "_get_file_whitelist() is deprecated and will be removed in a future version."
            "Use _get_file_allowlist() instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )

        mocked_get_file_allowlist.assert_called_once()

    # --------------------- deprecated methods END

    def test_init_regular(self):
        service = StructureTestValidator()

        self.assertEqual(service.file_allowlist, ["__init__"])
        self.assertEqual(service.issue_list, [])

    @override_settings(TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST=["my_file"])
    def test_get_file_allowlist_from_settings(self):
        service = StructureTestValidator()
        file_allowlist = service._get_file_allowlist()

        self.assertEqual(file_allowlist, ["__init__", "my_file"])

    def test_get_file_allowlist_fallback(self):
        service = StructureTestValidator()
        file_allowlist = service._get_file_allowlist()

        self.assertEqual(file_allowlist, ["__init__"])

    @override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR=settings.BASE_PATH)
    def test_get_base_dir_from_settings(self):
        service = StructureTestValidator()
        base_dir = service._get_base_dir()

        self.assertEqual(base_dir, settings.BASE_PATH)

    def test_get_base_dir_fallback(self):
        service = StructureTestValidator()
        base_dir = service._get_base_dir()

        self.assertEqual(base_dir, "")

    @override_settings(TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="my_project")
    def test_get_base_app_name_from_settings(self):
        service = StructureTestValidator()
        base_app_name = service._get_base_app_name()

        self.assertEqual(base_app_name, "my_project")

    def test_get_base_app_name_fallback(self):
        service = StructureTestValidator()
        base_app_name = service._get_base_app_name()

        self.assertEqual(base_app_name, "apps")

    @override_settings(TEST_STRUCTURE_VALIDATOR_APP_LIST=["apps.my_app", "apps.other_app"])
    def test_get_app_list_from_settings(self):
        service = StructureTestValidator()
        base_app_name = service._get_app_list()

        self.assertEqual(base_app_name, ["apps.my_app", "apps.other_app"])

    def test_get_app_list_fallback(self):
        service = StructureTestValidator()
        base_app_name = service._get_app_list()

        self.assertEqual(base_app_name, settings.INSTALLED_APPS)

    @override_settings(TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST=["my_dir", "other_dir"])
    def test_get_ignored_directory_list_from_settings(self):
        service = StructureTestValidator()
        dir_list = service._get_ignored_directory_list()

        self.assertEqual(dir_list, ["__pycache__", "my_dir", "other_dir"])

    def test_get_ignored_directory_list_fallback(self):
        service = StructureTestValidator()
        dir_list = service._get_ignored_directory_list()

        self.assertEqual(dir_list, ["__pycache__"])

    def test_check_missing_test_prefix_correct_prefix(self):
        service = StructureTestValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix",
            filename="test_my_file",
            extension=".py",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    @override_settings(TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST=["my_file"])
    def test_check_missing_test_prefix_wrong_prefix_but_allowlisted(self):
        service = StructureTestValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix",
            filename="my_file",
            extension=".py",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_test_prefix_wrong_prefix_but_not_py_file(self):
        service = StructureTestValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix",
            filename="missing_prefix",
            extension=".txt",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_test_prefix_wrong_prefix(self):
        service = StructureTestValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix",
            filename="missing_prefix",
            extension=".py",
        )

        self.assertFalse(result)
        self.assertEqual(len(service.issue_list), 1)

    def test_check_missing_init_init_found_files_in_dir(self):
        service = StructureTestValidator()
        result = service._check_missing_init(root="root/path", init_found=True, number_of_py_files=1)

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_init_no_init_no_files(self):
        service = StructureTestValidator()
        result = service._check_missing_init(root="root/path", init_found=False, number_of_py_files=0)

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_init_no_init_but_files(self):
        service = StructureTestValidator()
        result = service._check_missing_init(root="root/path", init_found=False, number_of_py_files=1)

        self.assertFalse(result)
        self.assertEqual(len(service.issue_list), 1)

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path("/src/ambient_toolbox/"),
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="my_project",
    )
    def test_build_path_to_test_package_with_settings_path(self):
        service = StructureTestValidator()
        path = service._build_path_to_test_package(app="my_project.my_app")

        self.assertEqual(path, Path("/src/ambient_toolbox/my_project/my_app/tests"))

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR="/src/ambient_toolbox/", TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="my_project"
    )
    def test_build_path_to_test_package_with_settings_str(self):
        service = StructureTestValidator()
        path = service._build_path_to_test_package(app="my_project.my_app")

        self.assertEqual(path, Path("/src/ambient_toolbox/my_project/my_app/tests"))

    def test_build_path_to_test_package_with_defaults(self):
        service = StructureTestValidator()
        path = service._build_path_to_test_package(app="my_project.my_app")

        self.assertEqual(path, Path("my_project/my_app/tests"))

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR=settings.BASE_PATH,
        TEST_STRUCTURE_VALIDATOR_APP_LIST=["testapp"],
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="",
    )
    def test_process_functional(self):
        service = StructureTestValidator()
        with self.assertRaises(SystemExit):
            service.process()

        self.assertEqual(len(service.issue_list), 2)

        complaint_list = sorted(service.issue_list)

        self.assertIn('Python file without "test_" prefix found:', complaint_list[0])
        self.assertIn("testapp/tests/subdirectory/missing_test_prefix.py", complaint_list[0])

        self.assertIn("__init__.py missing in", complaint_list[1])
        self.assertIn("testapp/tests/missing_init", complaint_list[1])

    @mock.patch.object(StructureTestValidator, "_get_app_list", return_value=["invalidly_located_app"])
    def test_process_invalidly_located_app(self, mocked_get_app_list):
        service = StructureTestValidator()

        service.process()

        mocked_get_app_list.assert_called_once()
