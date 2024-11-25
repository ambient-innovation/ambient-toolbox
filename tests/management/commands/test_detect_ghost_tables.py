import sys
from unittest import mock

from django.core.management import call_command
from django.db import connection
from django.test import SimpleTestCase


class DetectGhostTableCommandTest(SimpleTestCase):
    @mock.patch.object(connection.introspection, "table_names", return_value=["invalid_table"])
    def test_management_command_match_found(self, *args):
        with mock.patch.object(sys.stdout, "write") as mocked_write:
            call_command("detect_ghost_tables")

        mocked_write.assert_called_with("* invalid_table\n")

    @mock.patch.object(connection.introspection, "table_names", return_value=[])
    def test_management_no_match_found(self, *args):
        with mock.patch.object(sys.stdout, "write") as mocked_write:
            call_command("detect_ghost_tables")

        mocked_write.assert_not_called()
