import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Validates for all active languages (settings.LANGUAGES) the integrity of the PO translation files.
    The following cases are covered:
    * Fuzzy translations aren't allowed
    * Commented-out translations aren't allowed
    * Validate, that `manage.py makemessages` has been called before committing
    * Validate, that all translations were actually translated
    """

    OK_MESSAGE = "OK."

    def handle(self, *args, **options):
        for lang, label in settings.LANGUAGES:
            print(f'Check language "{label}"...')
            translation_file_path = f"./locale/{lang}/LC_MESSAGES/django.po"

            if not os.path.isfile(translation_file_path):
                print("> Skipping language due to missing PO file.")
                continue

            # Check for fuzzy translations
            print("> Check for fuzzy translations")
            output = subprocess.call(f'grep -q "#, fuzzy" {translation_file_path}', shell=True)
            if output == 0:
                raise Exception(f"Please remove all fuzzy translations in {translation_file_path}.")
            else:
                print(self.OK_MESSAGE)

            # Check for left-over translations
            print("> Check for left-over translations")
            output = subprocess.call(f'grep -q "#~" {translation_file_path}', shell=True)
            if output == 0:
                raise Exception(f"Please remove all commented-out translations in {translation_file_path}.")
            else:
                print(self.OK_MESSAGE)

            # Check if "makemessages" detects new translations
            print('> Check if "makemessages" detects new translations')
            subprocess.call(f"python manage.py create_translation_file --lang {lang}", shell=True)
            print(self.OK_MESSAGE)

            # Checking for differences in translation file
            print("> Checking for differences in translation file")
            output = subprocess.call(
                r"git diff --ignore-matching-lines=POT-Creation-Date --ignore-matching-lines=# --exit-code locale/",
                shell=True,
            )
            if output > 0:
                raise Exception(
                    "It seems you have forgotten to update your translation files before pushing your "
                    "changes.\nPlease run 'manage.py create_translation_file' and 'manage.py "
                    "compilemessages'."
                )
            else:
                print(self.OK_MESSAGE)

            # Check if all translation strings have been translated
            print("> Check if all translation strings have been translated")
            output = subprocess.call(
                f"msgattrib --untranslated ./locale/{lang}/LC_MESSAGES/django.po | exit `wc -c`", shell=True
            )
            if output > 0:
                raise Exception("You have untranslated strings in your translation files.")
            else:
                print(self.OK_MESSAGE)
