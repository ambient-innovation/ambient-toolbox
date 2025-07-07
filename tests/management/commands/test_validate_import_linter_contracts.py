from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

from ambient_toolbox.import_linter.services import ImportLinterContractService


class ValidateImportLinterContractsCommandTest(SimpleTestCase):
    @mock.patch.object(ImportLinterContractService, "validate_contracts", return_value=True)
    @mock.patch("sys.exit")
    def test_management_command_validation_successful(self, mocked_sys_exit, mocked_validate_contracts):
        call_command("validate_import_linter_contracts")

        mocked_validate_contracts.assert_called_with()
        mocked_sys_exit.assert_called_with(False)

    @mock.patch.object(ImportLinterContractService, "validate_contracts", return_value=False)
    @mock.patch("sys.exit")
    def test_management_command_validation_failure(self, mocked_sys_exit, mocked_validate_contracts):
        call_command("validate_import_linter_contracts")

        mocked_validate_contracts.assert_called_with()
        mocked_sys_exit.assert_called_with(True)
