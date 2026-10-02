from importlib import import_module as real_import
from types import ModuleType
from unittest.mock import patch

from django.test import TestCase, override_settings

from ambient_toolbox.system_checks.backend_imports import check_backend_env_variables, is_valid_python_path


class BackendImportsSystemCheckTest(TestCase):
    def test_check_backend_env_variables_no_backend_variables(self):
        """
        When no _BACKEND settings exist, no warnings should be returned.
        """
        # The default settings should be valid, so no warnings
        warnings = check_backend_env_variables()

        self.assertEqual(warnings, [])

    @override_settings(VALID_BACKEND="django.core.mail.backends.console.EmailBackend")
    def test_check_backend_env_variables_valid_backend(self):
        """
        When a valid _BACKEND setting exists, no warnings should be returned.
        """
        warnings = check_backend_env_variables()

        self.assertEqual(warnings, [])

    @override_settings(INVALID_BACKEND="non.existent.module.SomeClass")
    def test_check_backend_env_variables_invalid_module(self):
        """
        When a _BACKEND setting points to a non-existent module, a warning should be returned.
        """
        warnings = check_backend_env_variables()

        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].id, "ambient_toolbox.W006")
        self.assertIn("INVALID_BACKEND", warnings[0].msg)
        self.assertIn("non.existent.module.SomeClass", warnings[0].msg)

    @override_settings(INVALID_CLASS_BACKEND="django.core.mail.backends.console.NonExistentClass")
    def test_check_backend_env_variables_invalid_class(self):
        """
        When a _BACKEND setting points to a non-existent class in a valid module,
        a warning should be returned.
        """
        warnings = check_backend_env_variables()

        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].id, "ambient_toolbox.W005")
        self.assertIn("INVALID_CLASS_BACKEND", warnings[0].msg)
        self.assertIn("NonExistentClass", warnings[0].msg)

    @override_settings(MODULE_ONLY_BACKEND="nonexistent_module")
    def test_check_backend_env_variables_module_only_path(self):
        """
        When a _BACKEND setting is just a module name (no dots), it should try to import as a module.
        """
        warnings = check_backend_env_variables()

        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].id, "ambient_toolbox.W006")
        self.assertIn("MODULE_ONLY_BACKEND", warnings[0].msg)
        self.assertIn("nonexistent_module", warnings[0].msg)

    @patch("ambient_toolbox.system_checks.backend_imports.import_module")
    @override_settings(IMPORT_ERROR_BACKEND="some.module.Class")
    def test_check_backend_env_variables_import_error(self, mock_import):
        """
        When an ImportError (not ModuleNotFoundError) occurs during import, a warning should be returned.
        """

        # Make import_module raise ImportError for our specific backend
        def side_effect(module_name: str) -> ModuleType:
            if module_name == "some.module":
                raise ImportError
            # For other modules, use the real import_module
            return real_import(module_name)

        mock_import.side_effect = side_effect

        warnings = check_backend_env_variables()

        # Since we're only mocking one specific module, we should get exactly one warning
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].id, "ambient_toolbox.W007")
        self.assertIn("IMPORT_ERROR_BACKEND", warnings[0].msg)

    @override_settings(EMPTY_BACKEND="")
    def test_check_backend_env_variables_empty_value(self):
        """
        When a _BACKEND setting has an empty value, no warning should be returned.
        """
        warnings = check_backend_env_variables()

        self.assertEqual(warnings, [])

    @override_settings(INVALID_PATH_BACKEND="not a valid path")
    def test_check_backend_env_variables_invalid_path_format(self):
        """
        When a _BACKEND setting has an invalid path format, no warning should be returned.
        """
        warnings = check_backend_env_variables()

        self.assertEqual(warnings, [])

    @override_settings(
        VALID_BACKEND_1="django.core.mail.backends.console.EmailBackend",
        VALID_BACKEND_2="django.core.mail.backends.smtp.EmailBackend",
        INVALID_BACKEND="non.existent.module.Class",
    )
    def test_check_backend_env_variables_multiple_backends(self):
        """
        When multiple _BACKEND settings exist, only invalid ones should generate warnings.
        """
        warnings = check_backend_env_variables()

        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].id, "ambient_toolbox.W006")
        self.assertIn("INVALID_BACKEND", warnings[0].msg)

    def test_is_valid_python_path_returns_true_for_simple_module(self):
        self.assertIs(is_valid_python_path(path="my_module"), True)

    def test_is_valid_python_path_returns_true_for_dotted_module(self):
        self.assertIs(is_valid_python_path(path="django.core.mail"), True)

    def test_is_valid_python_path_returns_true_for_full_class_path(self):
        self.assertIs(is_valid_python_path(path="django.core.mail.backends.console.EmailBackend"), True)

    def test_is_valid_python_path_returns_true_for_nested_module(self):
        self.assertIs(is_valid_python_path(path="my_module.sub_module.MyClass"), True)

    def test_is_valid_python_path_returns_true_for_private_module(self):
        self.assertIs(is_valid_python_path(path="_private_module.MyClass"), True)

    def test_is_valid_python_path_returns_true_for_numeric_suffix(self):
        self.assertIs(is_valid_python_path(path="module123.Class456"), True)

    def test_is_valid_python_path_returns_false_for_empty_string(self):
        self.assertIs(is_valid_python_path(path=""), False)

    def test_is_valid_python_path_returns_false_for_single_dot(self):
        self.assertIs(is_valid_python_path(path="."), False)

    def test_is_valid_python_path_returns_false_for_leading_dot(self):
        self.assertIs(is_valid_python_path(path=".module"), False)

    def test_is_valid_python_path_returns_false_for_trailing_dot(self):
        self.assertIs(is_valid_python_path(path="module."), False)

    def test_is_valid_python_path_returns_false_for_consecutive_dots(self):
        self.assertIs(is_valid_python_path(path="module..submodule"), False)

    def test_is_valid_python_path_returns_false_for_hyphen(self):
        self.assertIs(is_valid_python_path(path="my-module"), False)

    def test_is_valid_python_path_returns_false_for_space(self):
        self.assertIs(is_valid_python_path(path="my module"), False)

    def test_is_valid_python_path_returns_false_for_slash(self):
        self.assertIs(is_valid_python_path(path="my/module"), False)

    def test_is_valid_python_path_returns_false_for_numeric_prefix(self):
        self.assertIs(is_valid_python_path(path="123module"), False)

    def test_is_valid_python_path_returns_false_for_numeric_prefix_in_part(self):
        self.assertIs(is_valid_python_path(path="module.123class"), False)
