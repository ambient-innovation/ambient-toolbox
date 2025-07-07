from pathlib import Path

from django.test import TestCase, override_settings

from ambient_toolbox.import_linter.settings import (
    get_import_linter_blocklisted_apps,
    get_import_linter_business_logic_apps,
    get_import_linter_local_apps,
    get_import_linter_path_to_toml,
    get_import_linter_root_packages,
)


class ImportLinterSettingsTests(TestCase):
    @override_settings(INSTALLED_APPS=["ambient_toolbox"])
    def test_get_import_linter_root_packages_default(self):
        self.assertEqual(get_import_linter_root_packages(), ["ambient_toolbox"])

    @override_settings(TOOLBOX_IMPORT_LINTER_ROOT_PACKAGES=["pkg1", "pkg2"])
    def test_get_import_linter_root_packages_override(self):
        self.assertEqual(get_import_linter_root_packages(), ["pkg1", "pkg2"])

    def test_get_import_linter_business_logic_apps_default(self):
        self.assertEqual(get_import_linter_business_logic_apps(), [])

    @override_settings(TOOLBOX_IMPORT_LINTER_BUSINESS_LOGIC_APPS=["logic_app"])
    def test_get_import_linter_business_logic_apps_override(self):
        self.assertEqual(get_import_linter_business_logic_apps(), ["logic_app"])

    def test_get_import_linter_blocklisted_apps_default(self):
        self.assertEqual(get_import_linter_blocklisted_apps(), [])

    @override_settings(TOOLBOX_IMPORT_LINTER_BLOCKLISTED_APPS=["blocked_app"])
    def test_get_import_linter_blocklisted_apps_override(self):
        self.assertEqual(get_import_linter_blocklisted_apps(), ["blocked_app"])

    @override_settings(INSTALLED_APPS=["ambient_toolbox"])
    def test_get_import_linter_local_apps_default(self):
        self.assertEqual(get_import_linter_local_apps(), ["ambient_toolbox"])

    @override_settings(TOOLBOX_IMPORT_LINTER_LOCAL_APPS=["local_app"])
    def test_get_import_linter_local_apps_override(self):
        self.assertEqual(get_import_linter_local_apps(), ["local_app"])

    def test_get_import_linter_path_to_toml_default(self):
        self.assertEqual(get_import_linter_path_to_toml(), Path("./pyproject.toml"))

    @override_settings(TOOLBOX_IMPORT_LINTER_PATH_TO_TOML=Path("/custom/path.toml"))
    def test_get_import_linter_path_to_toml_override(self):
        self.assertEqual(get_import_linter_path_to_toml(), Path("/custom/path.toml"))
