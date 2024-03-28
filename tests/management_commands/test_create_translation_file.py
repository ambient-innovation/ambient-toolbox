import os

from django.core.management import call_command
from django.test import SimpleTestCase

import settings


class CreateTranslationFileTest(SimpleTestCase):
    TEST_LANG = "xx"

    @classmethod
    def tearDownClass(cls):
        os.remove(settings.LOCALE_PATHS[0] / f"{cls.TEST_LANG}/LC_MESSAGES/django.po")

    def test_command_regular(self):
        call_command("create_translation_file", lang=self.TEST_LANG)

    def test_command_no_lang_param(self):
        with self.assertRaisesMessage(RuntimeError, 'Please provide a language with the "--lang" parameter.'):
            call_command("create_translation_file")
