from argparse import ArgumentParser
from unittest import mock

from django.test import TestCase
from django.test.utils import override_settings

from ambient_toolbox.management.commands.install_permission_fixtures import Command
from ambient_toolbox.permissions.fixtures.services import PermissionSetupService


class InstallPermissionFixturesCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_add_arguments_regular(self):
        command = Command()

        parser = ArgumentParser()

        command.add_arguments(parser)

        self.assertTrue("--dry-run" in [action.option_strings[0] for action in parser._actions])

    @override_settings(GROUP_PERMISSION_FIXTURES=["testapp.permissions.TestGroupDeclaration"])
    @mock.patch.object(PermissionSetupService, "process", return_value=([], []))
    def test_run_command_regular(self, mocked_process):
        command = Command()
        command.handle()

        mocked_process.assert_called_once()

    @mock.patch.object(PermissionSetupService, "process")
    def test_run_command_no_settings_variable(self, mocked_process):
        command = Command()
        command.handle()

        mocked_process.assert_not_called()

    @mock.patch.object(PermissionSetupService, "process")
    def test_run_command_dry_run(self, mocked_process):
        command = Command()
        command.handle(dry_run=True)

        mocked_process.assert_not_called()
