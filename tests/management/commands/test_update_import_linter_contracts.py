from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

from ambient_toolbox.import_linter.services import ImportLinterContractService


class UpdateImportLinterContractsCommandTest(SimpleTestCase):
    @mock.patch.object(ImportLinterContractService, "update_contracts")
    def test_management_command_called(self, mocked_update_contracts):
        call_command("update_import_linter_contracts")

        mocked_update_contracts.assert_called_with()
