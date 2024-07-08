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

    def handle(self, *args, **options):
        for lang, label in settings.LANGUAGES:
            print(f'Check language "{label}"...')

            if not os.path.isfile(f"./locale/{lang}/LC_MESSAGES/django.po"):
                print("> Skipping language due to missing PO file.")
                continue

            # Check for fuzzy translations
            print("> Check for fuzzy translations")
            output = subprocess.call(f'grep -q "#, fuzzy" ./locale/{lang}/LC_MESSAGES/django.po', shell=True)
            if output == 0:
                raise Exception("Please remove all fuzzy translations in your translation files.")
            else:
                print("OK.")

            # Check for left-over translations
            print("> Check for left-over translations")
            output = subprocess.call(f'grep -q "#~" ./locale/{lang}/LC_MESSAGES/django.po', shell=True)
            if output == 0:
                raise Exception("Please remove all commented-out translations in your translation files.")
            else:
                print("OK.")

            # Check if "makemessages" detects new translations
            print('> Check if "makemessages" detects new translations')
            subprocess.call(f"python manage.py create_translation_file --lang {lang}", shell=True)
            print("OK.")

            # Checking for differences in translation file
            print("> Checking for differences in translation file")
            output = subprocess.call(
                r"git diff --ignore-matching-lines=POT-Creation-Date --ignore-matching-lines=# --exit-code locale/",
                shell=True,
            )
            if output > 0:
                raise Exception(
                    "It seems you have forgotten to update your translation file before pushing your changes."
                )
            else:
                print("OK.")

            # Check if all translation strings have been translated
            print("> Check if all translation strings have been translated")
            output = subprocess.call(
                f"msgattrib --untranslated ./locale/{lang}/LC_MESSAGES/django.po | exit `wc -c`", shell=True
            )
            if output > 0:
                raise Exception("You have untranslated strings in your translation files.")
            else:
                print("OK.")
