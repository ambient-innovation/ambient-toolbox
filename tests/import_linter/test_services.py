import shutil
import tempfile
from pathlib import Path

from django.test import TestCase, override_settings

from ambient_toolbox.import_linter.services import ImportLinterContractService


class ImportLinterContractServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp())
        cls.toml_path = cls.tmp_dir / "pyproject.toml"
        cls.toml_path.write_text(
            """
[tool.importlinter]
root_packages = ["app1", "app2"]
include_external_packages = true

[[tool.importlinter.contracts]]
name = "existing contract"
type = "forbidden"
source_modules = "foo"
forbidden_modules = ["bar"]
            """.strip(),
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_dir)

    @override_settings(
        TOOLBOX_IMPORT_LINTER_PATH_TO_TOML=None,  # Wird in `test_class_instantiates_correctly` gesetzt
        TOOLBOX_IMPORT_LINTER_ROOT_PACKAGES=["app1", "app2", "block"],
        TOOLBOX_IMPORT_LINTER_BLOCKLISTED_APPS=["block"],
        TOOLBOX_IMPORT_LINTER_LOCAL_APPS=["app1", "app2", "block"],
        TOOLBOX_IMPORT_LINTER_BUSINESS_LOGIC_APPS=["app1"],
    )
    def test_class_instantiates_correctly(self):
        with override_settings(TOOLBOX_IMPORT_LINTER_PATH_TO_TOML=self.toml_path):
            service = ImportLinterContractService()

            self.assertEqual(service.root_packages, ["app1", "app2", "block"])
            self.assertEqual(service.blocklisted_apps, ["block"])
            self.assertEqual(service.business_logic_apps, ["app1"])
            self.assertEqual(service.local_django_apps, ["app1", "app2", "block"])
            self.assertEqual(service.path_to_toml, self.toml_path)

    @override_settings(TOOLBOX_IMPORT_LINTER_PATH_TO_TOML=Path("/nonexistent/pyproject.toml"))
    def test_load_toml_file_missing_raises(self):
        service = ImportLinterContractService()
        with self.assertRaises(RuntimeError) as cm:
            service._load_toml_from_pyproject_file()
        self.assertIn("does not exist", str(cm.exception))

    def test_load_toml_invalid_raises(self):
        invalid_file = self.tmp_dir / "broken.toml"
        invalid_file.write_text("this = [invalid", encoding="utf-8")
        with override_settings(TOOLBOX_IMPORT_LINTER_PATH_TO_TOML=invalid_file):
            service = ImportLinterContractService()
            with self.assertRaises(RuntimeError) as cm:
                service._load_toml_from_pyproject_file()
            self.assertIn("is invalid", str(cm.exception))

    @override_settings(
        TOOLBOX_IMPORT_LINTER_PATH_TO_TOML=None,
        TOOLBOX_IMPORT_LINTER_ROOT_PACKAGES=["app1", "app2", "block"],
        TOOLBOX_IMPORT_LINTER_BLOCKLISTED_APPS=["block"],
        TOOLBOX_IMPORT_LINTER_LOCAL_APPS=["app1", "app2", "block"],
        TOOLBOX_IMPORT_LINTER_BUSINESS_LOGIC_APPS=["app1"],
    )
    def test_update_contracts_writes_expected_content(self):
        with override_settings(TOOLBOX_IMPORT_LINTER_PATH_TO_TOML=self.toml_path):
            service = ImportLinterContractService()
            service.update_contracts()

            content = self.toml_path.read_text(encoding="utf-8")
            assert "[GENERATED] Independent app 'app2' not allowed to know about other apps" in content
            assert "existing contract" in content  # Existing contracts stay

    @override_settings(
        TOOLBOX_IMPORT_LINTER_PATH_TO_TOML=None,
        TOOLBOX_IMPORT_LINTER_ROOT_PACKAGES=["app1"],
        TOOLBOX_IMPORT_LINTER_LOCAL_APPS=["app1"],
        TOOLBOX_IMPORT_LINTER_BLOCKLISTED_APPS=[],
        TOOLBOX_IMPORT_LINTER_BUSINESS_LOGIC_APPS=["app1"],
    )
    def test_validate_contracts_returns_true_when_nothing_changes(self):
        # Write current status
        with override_settings(TOOLBOX_IMPORT_LINTER_PATH_TO_TOML=self.toml_path):
            service = ImportLinterContractService()
            service.update_contracts()

            # Reevaluation should return True
            service = ImportLinterContractService()
            self.assertTrue(service.validate_contracts())
