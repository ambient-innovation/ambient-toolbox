from os.path import isfile

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase


class CreateTranslationFileTest(SimpleTestCase):
    def test_command_regular(self):
        call_command("create_translation_file", lang="xx")

        self.assertTrue(isfile(settings.LOCALE_PATHS[0] / "xx/LC_MESSAGES/django.po"))
