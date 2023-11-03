from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings

from ambient_toolbox.tests.structure_validator.test_structure_validator import TestStructureValidator


class TestStructureValidatorTest(TestCase):
    def test_init_regular(self):
        service = TestStructureValidator()

        self.assertEqual(service.file_whitelist, ["__init__"])
        self.assertEqual(service.issue_list, [])

    @override_settings(TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST=["my_file"])
    def test_get_file_whitelist_from_settings(self):
        service = TestStructureValidator()
        file_whitelist = service._get_file_whitelist()

        self.assertEqual(file_whitelist, ["__init__", "my_file"])

    def test_get_file_whitelist_fallback(self):
        service = TestStructureValidator()
        file_whitelist = service._get_file_whitelist()

        self.assertEqual(file_whitelist, ["__init__"])

    @override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR=settings.BASE_PATH)
    def test_get_base_dir_from_settings(self):
        service = TestStructureValidator()
        base_dir = service._get_base_dir()

        self.assertEqual(base_dir, settings.BASE_PATH)

    def test_get_base_dir_fallback(self):
        service = TestStructureValidator()
        base_dir = service._get_base_dir()

        self.assertEqual(base_dir, "")

    @override_settings(TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="my_project")
    def test_get_base_app_name_from_settings(self):
        service = TestStructureValidator()
        base_app_name = service._get_base_app_name()

        self.assertEqual(base_app_name, "my_project")

    def test_get_base_app_name_fallback(self):
        service = TestStructureValidator()
        base_app_name = service._get_base_app_name()

        self.assertEqual(base_app_name, "apps")

    @override_settings(TEST_STRUCTURE_VALIDATOR_APP_LIST=["apps.my_app", "apps.other_app"])
    def test_get_app_list_from_settings(self):
        service = TestStructureValidator()
        base_app_name = service._get_app_list()

        self.assertEqual(base_app_name, ["apps.my_app", "apps.other_app"])

    def test_get_app_list_fallback(self):
        service = TestStructureValidator()
        base_app_name = service._get_app_list()

        self.assertEqual(base_app_name, settings.INSTALLED_APPS)

    @override_settings(TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST=["my_dir", "other_dir"])
    def test_get_ignored_directory_list_from_settings(self):
        service = TestStructureValidator()
        dir_list = service._get_ignored_directory_list()

        self.assertEqual(dir_list, ["__pycache__", "my_dir", "other_dir"])

    def test_get_ignored_directory_list_fallback(self):
        service = TestStructureValidator()
        dir_list = service._get_ignored_directory_list()

        self.assertEqual(dir_list, ["__pycache__"])

    def test_check_missing_test_prefix_correct_prefix(self):
        service = TestStructureValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix",
            filename="test_my_file",
            extension=".py",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    @override_settings(TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST=["my_file"])
    def test_check_missing_test_prefix_wrong_prefix_but_whitelisted(self):
        service = TestStructureValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix",
            filename="my_file",
            extension=".py",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_test_prefix_wrong_prefix_but_not_py_file(self):
        service = TestStructureValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix",
            filename="missing_prefix",
            extension=".txt",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_test_prefix_wrong_prefix(self):
        service = TestStructureValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix",
            filename="missing_prefix",
            extension=".py",
        )

        self.assertFalse(result)
        self.assertEqual(len(service.issue_list), 1)

    def test_check_missing_init_init_found_files_in_dir(self):
        service = TestStructureValidator()
        result = service._check_missing_init(root="root/path", init_found=True, number_of_py_files=1)

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_init_no_init_no_files(self):
        service = TestStructureValidator()
        result = service._check_missing_init(root="root/path", init_found=False, number_of_py_files=0)

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_init_no_init_but_files(self):
        service = TestStructureValidator()
        result = service._check_missing_init(root="root/path", init_found=False, number_of_py_files=1)

        self.assertFalse(result)
        self.assertEqual(len(service.issue_list), 1)

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path("/src/ambient_toolbox/"),
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="my_project",
    )
    def test_build_path_to_test_package_with_settings_path(self):
        service = TestStructureValidator()
        path = service._build_path_to_test_package(app="my_project.my_app")

        self.assertEqual(path, Path("/src/ambient_toolbox/my_project/my_app/tests"))

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR="/src/ambient_toolbox/", TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="my_project"
    )
    def test_build_path_to_test_package_with_settings_str(self):
        service = TestStructureValidator()
        path = service._build_path_to_test_package(app="my_project.my_app")

        self.assertEqual(path, Path("/src/ambient_toolbox/my_project/my_app/tests"))

    def test_build_path_to_test_package_with_defaults(self):
        service = TestStructureValidator()
        path = service._build_path_to_test_package(app="my_project.my_app")

        self.assertEqual(path, Path("my_project/my_app/tests"))

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR=settings.BASE_PATH,
        TEST_STRUCTURE_VALIDATOR_APP_LIST=["testapp"],
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="",
    )
    def test_process_functional(self):
        service = TestStructureValidator()
        with self.assertRaises(SystemExit):
            service.process()

        self.assertEqual(len(service.issue_list), 2)

        complaint_list = sorted(service.issue_list)

        self.assertIn('Python file without "test_" prefix found:', complaint_list[0])
        self.assertIn("testapp/tests/subdirectory/missing_test_prefix.py", complaint_list[0])

        self.assertIn("__init__.py missing in", complaint_list[1])
        self.assertIn("testapp/tests/missing_init", complaint_list[1])

    @mock.patch.object(TestStructureValidator, "_get_app_list", return_value=["invalidly_located_app"])
    def test_process_invalidly_located_app(self, mocked_get_app_list):
        service = TestStructureValidator()

        service.process()

        mocked_get_app_list.assert_called_once()
