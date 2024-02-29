from os.path import isfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase


class CreateTranslationFileTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Path(settings.LOCALE_PATHS[0] / "xx/LC_MESSAGES").mkdir(parents=True, exist_ok=True)

    def test_command_regular(self):
        call_command("create_translation_file", lang="xx")

        self.assertTrue(isfile(settings.LOCALE_PATHS[0] / "xx/LC_MESSAGES/django.po"))
