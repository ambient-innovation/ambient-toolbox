import os
import shutil
import subprocess
import tempfile

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Validates the integrity of PO translation files for every active language in ``settings.LANGUAGES``.

    The following checks are performed:

    * No fuzzy translations remain
    * No commented-out (obsolete) translations remain
    * ``manage.py makemessages`` has been run (no uncommitted string changes)
    * All translation strings have actually been translated
    """

    help = "Validates PO translation file integrity for all active languages."

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

            # Back up the PO file before regenerating so we can compare without requiring a git working tree
            fd, backup_file = tempfile.mkstemp(suffix=".po")
            os.close(fd)
            shutil.copy2(translation_file_path, backup_file)
            output = 0
            try:
                subprocess.call(f"python manage.py create_translation_file --lang {lang}", shell=True)
                print(self.OK_MESSAGE)

                # Checking for differences in translation file
                print("> Checking for differences in translation file")
                output = subprocess.call(
                    f"git diff --no-index --ignore-matching-lines=POT-Creation-Date --ignore-matching-lines=#"
                    f" --exit-code {backup_file} {translation_file_path}",
                    shell=True,
                )
            finally:
                shutil.copy2(backup_file, translation_file_path)
                os.unlink(backup_file)

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
