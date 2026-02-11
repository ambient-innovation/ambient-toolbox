"""
Comprehensive tests for StructureTestValidator.

This module tests all functionality of the StructureTestValidator class,
ensuring 100% code coverage and proper validation of test directory structures.
"""

import io
import sys
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings

from ambient_toolbox.tests.structure_validator.test_structure_validator import StructureTestValidator


# Test matrix will create invalid files which we want to ignore
@override_settings(TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST=[".tox"])
class TestStructureValidatorTest(TestCase):
    """Test cases for StructureTestValidator class."""

    # ============================================================================
    # Initialization Tests
    # ============================================================================

    def test_init_regular(self):
        """Test that initialization sets correct default values."""
        service = StructureTestValidator()

        self.assertEqual(service.file_allowlist, ["__init__"])
        self.assertEqual(service.file_whitelist, ["__init__"])
        self.assertEqual(service.issue_list, [])

    # ============================================================================
    # File Whitelist Tests
    # ============================================================================

    @override_settings(TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST=["my_file"])
    def test_get_file_allowlist_from_settings(self):
        """Test file allowlist retrieval from Django settings."""
        service = StructureTestValidator()
        file_allowlist = service._get_file_allowlist()

        self.assertEqual(file_allowlist, ["__init__", "my_file"])

    def test_get_file_allowlist_fallback(self):
        """Test file allowlist fallback to toolbox settings."""
        service = StructureTestValidator()
        file_allowlist = service._get_file_allowlist()

        self.assertEqual(file_allowlist, ["__init__"])

    # ============================================================================
    # Base Directory Tests
    # ============================================================================

    @override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR=settings.BASE_PATH)
    def test_get_base_dir_from_settings(self):
        """Test base directory retrieval from Django settings."""
        service = StructureTestValidator()
        base_dir = service._get_base_dir()

        self.assertEqual(base_dir, settings.BASE_PATH)

    def test_get_base_dir_fallback(self):
        """Test base directory fallback to toolbox settings."""
        # Save the original value if it exists
        original_value = getattr(settings, "TEST_STRUCTURE_VALIDATOR_BASE_DIR", None)
        has_original = hasattr(settings, "TEST_STRUCTURE_VALIDATOR_BASE_DIR")

        try:
            # Delete the setting to test fallback behavior
            if has_original:
                del settings.TEST_STRUCTURE_VALIDATOR_BASE_DIR

            service = StructureTestValidator()
            base_dir = service._get_base_dir()

            self.assertEqual(base_dir, "")
        finally:
            # Restore the original value if it existed
            if has_original:
                settings.TEST_STRUCTURE_VALIDATOR_BASE_DIR = original_value

    # ============================================================================
    # Base App Name Tests
    # ============================================================================

    @override_settings(TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="my_project")
    def test_get_base_app_name_from_settings(self):
        """Test base app name retrieval from Django settings."""
        service = StructureTestValidator()
        base_app_name = service._get_base_app_name()

        self.assertEqual(base_app_name, "my_project")

    def test_get_base_app_name_fallback(self):
        """Test base app name fallback to toolbox settings."""
        service = StructureTestValidator()
        base_app_name = service._get_base_app_name()

        self.assertEqual(base_app_name, "apps")

    # ============================================================================
    # App List Tests
    # ============================================================================

    @override_settings(TEST_STRUCTURE_VALIDATOR_APP_LIST=["apps.my_app", "apps.other_app"])
    def test_get_app_list_from_settings(self):
        """Test app list retrieval from Django settings."""
        service = StructureTestValidator()
        app_list = service._get_app_list()

        self.assertEqual(app_list, ["apps.my_app", "apps.other_app"])

    def test_get_app_list_fallback(self):
        """Test app list fallback to INSTALLED_APPS."""
        service = StructureTestValidator()
        app_list = service._get_app_list()

        self.assertEqual(app_list, settings.INSTALLED_APPS)

    # ============================================================================
    # Ignored Directory List Tests
    # ============================================================================

    @override_settings(TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST=["my_dir", "other_dir"])
    def test_get_ignored_directory_list_from_settings(self):
        """Test ignored directory list retrieval from Django settings."""
        service = StructureTestValidator()
        dir_list = service._get_ignored_directory_list()

        self.assertEqual(dir_list, ["__pycache__", ".venv", "venv", "env", "my_dir", "other_dir"])

    def test_get_ignored_directory_list_fallback(self):
        """Test ignored directory list fallback to toolbox settings."""
        # Delete the attribute to ensure we trigger the fallback path
        original_value = getattr(settings, "TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST", None)
        has_original = hasattr(settings, "TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST")

        try:
            if has_original:
                del settings.TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST

            service = StructureTestValidator()
            dir_list = service._get_ignored_directory_list()

            self.assertIn("__pycache__", dir_list)
        finally:
            if has_original:
                settings.TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST = original_value

    # ============================================================================
    # Misplaced Test File Whitelist Tests
    # ============================================================================

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_ALLOWLIST=["handlers/commands", "special_tests"]
    )
    def test_get_misplaced_test_file_allowlist_from_settings(self):
        """Test misplaced test file allowlist retrieval from Django settings."""
        service = StructureTestValidator()
        allowlist = service._get_misplaced_test_file_allowlist()

        self.assertEqual(allowlist, ["handlers/commands", "special_tests"])

    def test_get_misplaced_test_file_allowlist_fallback(self):
        """Test misplaced test file allowlist fallback to toolbox settings."""
        service = StructureTestValidator()
        allowlist = service._get_misplaced_test_file_allowlist()

        self.assertEqual(allowlist, [])

    # ============================================================================
    # Check Missing Test Prefix Tests
    # ============================================================================

    def test_check_missing_test_prefix_correct_prefix(self):
        """Test that files with correct 'test_' prefix pass validation."""
        service = StructureTestValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="test_my_file.py",
            filename="test_my_file",
            extension=".py",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    @override_settings(TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST=["my_file"])
    def test_check_missing_test_prefix_allowlisted_file(self):
        """Test that allowlisted files without 'test_' prefix pass validation."""
        service = StructureTestValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="my_file.py",
            filename="my_file",
            extension=".py",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_test_prefix_non_python_file(self):
        """Test that non-Python files pass validation regardless of prefix."""
        service = StructureTestValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix.txt",
            filename="missing_prefix",
            extension=".txt",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_test_prefix_missing_prefix(self):
        """Test that Python files without 'test_' prefix fail validation."""
        service = StructureTestValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="missing_prefix.py",
            filename="missing_prefix",
            extension=".py",
        )

        self.assertFalse(result)
        self.assertEqual(len(service.issue_list), 1)
        self.assertIn('Python file without "test_" prefix found:', service.issue_list[0])
        self.assertIn("root/path/missing_prefix.py", service.issue_list[0])

    def test_check_missing_test_prefix_init_file(self):
        """Test that __init__.py files are automatically included in the allowlist."""
        service = StructureTestValidator()
        result = service._check_missing_test_prefix(
            root="root/path",
            file="__init__.py",
            filename="__init__",
            extension=".py",
        )

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    # ============================================================================
    # Check Missing Init Tests
    # ============================================================================

    def test_check_missing_init_with_init_and_files(self):
        """Test that directories with __init__.py and Python files pass validation."""
        service = StructureTestValidator()
        result = service._check_missing_init(root="root/path", init_found=True, number_of_py_files=1)

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_init_no_init_no_files(self):
        """Test that empty directories (no init, no files) pass validation."""
        service = StructureTestValidator()
        result = service._check_missing_init(root="root/path", init_found=False, number_of_py_files=0)

        self.assertTrue(result)
        self.assertEqual(len(service.issue_list), 0)

    def test_check_missing_init_no_init_with_files(self):
        """Test that directories with Python files but no __init__.py fail validation."""
        service = StructureTestValidator()
        result = service._check_missing_init(root="root/path", init_found=False, number_of_py_files=1)

        self.assertFalse(result)
        self.assertEqual(len(service.issue_list), 1)
        self.assertIn("__init__.py missing in", service.issue_list[0])
        self.assertIn("root/path", service.issue_list[0])

    def test_check_missing_init_multiple_files(self):
        """Test validation with multiple Python files in directory."""
        service = StructureTestValidator()
        result = service._check_missing_init(root="root/path", init_found=False, number_of_py_files=5)

        self.assertFalse(result)
        self.assertEqual(len(service.issue_list), 1)

    # ============================================================================
    # Check Misplaced Test Files Tests
    # ============================================================================

    def test_check_misplaced_test_files_in_tests_directory(self):
        """Test that test files in 'tests' directory are not flagged as misplaced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a proper test structure
            tests_dir = Path(tmpdir) / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / "test_example.py"
            test_file.write_text("# Test file")

            with override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir)):
                service = StructureTestValidator()
                service._check_misplaced_test_files()

                self.assertEqual(len(service.issue_list), 0)

    def test_check_misplaced_test_files_outside_tests_directory(self):
        """Test that test files outside 'tests' directory are flagged as misplaced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a misplaced test file
            test_file = Path(tmpdir) / "test_misplaced.py"
            test_file.write_text("# Misplaced test file")

            with override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir)):
                service = StructureTestValidator()
                service._check_misplaced_test_files()

                self.assertEqual(len(service.issue_list), 1)
                self.assertIn("Test file found outside tests directory:", service.issue_list[0])
                self.assertIn("test_misplaced.py", service.issue_list[0])

    def test_check_misplaced_test_files_with_allowlist(self):
        """Test that allowlisted paths are not flagged even when outside tests directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file in an allowlisted location
            handlers_dir = Path(tmpdir) / "handlers"
            handlers_dir.mkdir()
            test_file = handlers_dir / "test_handler.py"
            test_file.write_text("# Handler test")

            with override_settings(
                TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir),
                TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST=["handlers"],
            ):
                service = StructureTestValidator()
                service._check_misplaced_test_files()

                self.assertEqual(len(service.issue_list), 0)

    def test_check_misplaced_test_files_ignores_pycache(self):
        """Test that __pycache__ directories are ignored during validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file in __pycache__ (should be ignored)
            pycache_dir = Path(tmpdir) / "__pycache__"
            pycache_dir.mkdir()
            test_file = pycache_dir / "test_cached.py"
            test_file.write_text("# Cached test")

            with override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir)):
                service = StructureTestValidator()
                service._check_misplaced_test_files()

                # Should not find the test file in __pycache__
                self.assertEqual(len(service.issue_list), 0)

    def test_check_misplaced_test_files_nested_tests_directory(self):
        """Test that test files in nested 'tests' directories are valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a nested tests structure
            app_dir = Path(tmpdir) / "myapp"
            app_dir.mkdir()
            tests_dir = app_dir / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / "test_nested.py"
            test_file.write_text("# Nested test file")

            with override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir)):
                service = StructureTestValidator()
                service._check_misplaced_test_files()

                self.assertEqual(len(service.issue_list), 0)

    def test_check_misplaced_test_files_non_test_files_ignored(self):
        """Test that files not starting with 'test_' are not flagged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a non-test Python file outside tests directory
            normal_file = Path(tmpdir) / "module.py"
            normal_file.write_text("# Normal module")

            with override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir)):
                service = StructureTestValidator()
                service._check_misplaced_test_files()

                self.assertEqual(len(service.issue_list), 0)

    def test_check_misplaced_test_files_non_python_files_ignored(self):
        """Test that non-Python files are not flagged even if they start with 'test_'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a non-Python file that starts with test_
            text_file = Path(tmpdir) / "test_data.txt"
            text_file.write_text("Test data")

            with override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir)):
                service = StructureTestValidator()
                service._check_misplaced_test_files()

                self.assertEqual(len(service.issue_list), 0)

    # ============================================================================
    # Build Path Tests
    # ============================================================================

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path("/src/ambient_toolbox/"),
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="my_project",
    )
    def test_build_path_to_test_package_with_path_object(self):
        """Test path building with Path object as base directory."""
        service = StructureTestValidator()
        path = service._build_path_to_test_package(app="my_project.my_app")

        self.assertEqual(path, Path("/src/ambient_toolbox/my_project/my_app/tests"))

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR="/src/ambient_toolbox/",
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="my_project",
    )
    def test_build_path_to_test_package_with_string(self):
        """Test path building with string as base directory."""
        service = StructureTestValidator()
        path = service._build_path_to_test_package(app="my_project.my_app")

        self.assertEqual(path, Path("/src/ambient_toolbox/my_project/my_app/tests"))

    @override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR="/src/")
    def test_build_path_to_test_package_with_default_app_name(self):
        """Test path building with default app name."""
        service = StructureTestValidator()
        path = service._build_path_to_test_package(app="my_project.my_app")

        self.assertEqual(path, Path("/src/my_project/my_app/tests"))

    def test_build_path_to_test_package_with_nested_app(self):
        """Test path building with deeply nested app structure."""
        with override_settings(TEST_STRUCTURE_VALIDATOR_BASE_DIR="/src/"):
            service = StructureTestValidator()
            path = service._build_path_to_test_package(app="my_project.apps.core.utils")

            self.assertEqual(path, Path("/src/my_project/apps/core/utils/tests"))

    # ============================================================================
    # Process Method Tests (Functional Tests)
    # ============================================================================

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR=settings.BASE_PATH,
        TEST_STRUCTURE_VALIDATOR_APP_LIST=["testapp"],
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="",
    )
    def test_process_with_multiple_issues(self):
        """Test process method identifies all types of issues."""
        service = StructureTestValidator()
        with self.assertRaises(SystemExit) as cm:
            service.process()

        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(len(service.issue_list), 4)

        complaint_list = sorted(service.issue_list)

        self.assertIn('Python file without "test_" prefix found:', complaint_list[0])
        self.assertIn("testapp/tests/subdirectory/missing_test_prefix.py", complaint_list[0])

        self.assertIn("Test file found outside tests directory:", complaint_list[1])
        self.assertIn("testapp/handlers/commands/test_commands.py", complaint_list[1])

        self.assertIn("Test file found outside tests directory:", complaint_list[2])
        self.assertIn("testapp/test_wrongly_placed_file.py", complaint_list[2])

        self.assertIn("__init__.py missing in", complaint_list[3])
        self.assertIn("testapp/tests/missing_init", complaint_list[3])

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR=settings.BASE_PATH,
        TEST_STRUCTURE_VALIDATOR_APP_LIST=["testapp"],
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="",
        TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST=["handlers/commands"],
    )
    def test_process_with_allowlist(self):
        """Test that allowlisted paths are not reported as issues."""
        service = StructureTestValidator()
        with self.assertRaises(SystemExit) as cm:
            service.process()

        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(len(service.issue_list), 3)

        complaint_list = sorted(service.issue_list)

        self.assertIn('Python file without "test_" prefix found:', complaint_list[0])
        self.assertIn("testapp/tests/subdirectory/missing_test_prefix.py", complaint_list[0])

        self.assertIn("Test file found outside tests directory:", complaint_list[1])
        self.assertIn("testapp/test_wrongly_placed_file.py", complaint_list[1])

        self.assertIn("__init__.py missing in", complaint_list[2])
        self.assertIn("testapp/tests/missing_init", complaint_list[2])

    @mock.patch.object(StructureTestValidator, "_get_app_list", return_value=["invalidly_located_app"])
    def test_process_skips_non_matching_apps(self, mocked_get_app_list):
        """Test that apps not starting with base app name are skipped."""
        service = StructureTestValidator()

        with self.assertRaises(SystemExit):
            service.process()

        mocked_get_app_list.assert_called_once()
        # Should only find misplaced test files, not any app-specific issues
        self.assertEqual(len(service.issue_list), 2)

    def test_process_success_no_issues(self):
        """Test process method succeeds when no issues are found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid test structure
            app_dir = Path(tmpdir) / "myapp"
            app_dir.mkdir()
            tests_dir = app_dir / "tests"
            tests_dir.mkdir()

            # Add __init__.py
            init_file = tests_dir / "__init__.py"
            init_file.write_text("")

            # Add a proper test file
            test_file = tests_dir / "test_example.py"
            test_file.write_text("# Test file")

            with override_settings(
                TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir),
                TEST_STRUCTURE_VALIDATOR_APP_LIST=["myapp"],
                TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="",
            ):
                service = StructureTestValidator()
                # Should not raise SystemExit
                service.process()

                self.assertEqual(len(service.issue_list), 0)

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR=settings.BASE_PATH,
        TEST_STRUCTURE_VALIDATOR_APP_LIST=[],
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="",
    )
    def test_process_with_empty_app_list(self):
        """Test process method with empty app list."""
        service = StructureTestValidator()
        # Should only check for misplaced test files
        with self.assertRaises(SystemExit):
            service.process()

        # Should find misplaced test files
        self.assertGreater(len(service.issue_list), 0)

    def test_process_prints_output(self):
        """Test that process method prints appropriate output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid structure
            app_dir = Path(tmpdir) / "testapp"
            app_dir.mkdir()
            tests_dir = app_dir / "tests"
            tests_dir.mkdir()
            init_file = tests_dir / "__init__.py"
            init_file.write_text("")
            test_file = tests_dir / "test_valid.py"
            test_file.write_text("# Test")

            with override_settings(
                TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir),
                TEST_STRUCTURE_VALIDATOR_APP_LIST=["testapp"],
                TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="",
            ):
                service = StructureTestValidator()

                # Capture stdout
                captured_output = io.StringIO()
                old_stdout = sys.stdout
                sys.stdout = captured_output

                try:
                    service.process()
                    output = captured_output.getvalue()

                    # Check for expected output messages
                    self.assertIn("Inspecting", output)
                    self.assertIn("0 issues detected. Yeah!", output)
                finally:
                    sys.stdout = old_stdout

    def test_process_with_pycache_directory(self):
        """Test that __pycache__ directories are properly ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "myapp"
            app_dir.mkdir()
            tests_dir = app_dir / "tests"
            tests_dir.mkdir()

            # Create __pycache__ directory
            pycache_dir = tests_dir / "__pycache__"
            pycache_dir.mkdir()

            # Add a file in __pycache__ (should be ignored)
            cached_file = pycache_dir / "test_cached.pyc"
            cached_file.write_text("")

            # Add proper files
            init_file = tests_dir / "__init__.py"
            init_file.write_text("")
            test_file = tests_dir / "test_example.py"
            test_file.write_text("# Test")

            with override_settings(
                TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir),
                TEST_STRUCTURE_VALIDATOR_APP_LIST=["myapp"],
                TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="",
            ):
                service = StructureTestValidator()
                service.process()

                # Should not find any issues
                self.assertEqual(len(service.issue_list), 0)

    @override_settings(
        TEST_STRUCTURE_VALIDATOR_BASE_DIR=settings.BASE_PATH,
        TEST_STRUCTURE_VALIDATOR_APP_LIST=["testapp"],
        TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="testapp",
    )
    def test_process_filters_by_base_app_name(self):
        """Test that only apps starting with base app name are processed."""
        service = StructureTestValidator()

        with self.assertRaises(SystemExit):
            service.process()

        # Should process testapp since it matches the base app name
        self.assertGreater(len(service.issue_list), 0)

    def test_process_with_non_python_files(self):
        """Test that process method handles non-Python files correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "myapp"
            app_dir.mkdir()
            tests_dir = app_dir / "tests"
            tests_dir.mkdir()

            # Add __init__.py
            init_file = tests_dir / "__init__.py"
            init_file.write_text("")

            # Add a Python test file
            test_file = tests_dir / "test_example.py"
            test_file.write_text("# Test")

            # Add non-Python files
            readme_file = tests_dir / "README.md"
            readme_file.write_text("# Tests")

            data_file = tests_dir / "test_data.json"
            data_file.write_text('{"key": "value"}')

            with override_settings(
                TEST_STRUCTURE_VALIDATOR_BASE_DIR=Path(tmpdir),
                TEST_STRUCTURE_VALIDATOR_APP_LIST=["myapp"],
                TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME="",
            ):
                service = StructureTestValidator()
                service.process()

                # Should not find any issues - non-Python files should be ignored
                self.assertEqual(len(service.issue_list), 0)
