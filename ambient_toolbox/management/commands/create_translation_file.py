from os.path import isfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Wrapper command for "makemessages" to remove "POT-Creation-Date:" which will cause countless merge conflicts.
    """

    help = "Creates translation files without merge-conflict-prone POT-Creation-Date headers."

    def add_arguments(self, parser):
        parser.add_argument("--lang", type=str)

    def detect_single_translation_language(self) -> str | None:
        """
        Returns the language code of the projects' translation if there is exactly one.
        Returns None otherwise.
        """
        locale_path = settings.LOCALE_PATHS[0]

        # We don't bother with odd configurations for a convenience feature
        if not isinstance(locale_path, Path):
            return None

        dir_list: list[Path] = [directory for directory in locale_path.iterdir() if directory.is_dir()]

        if len(dir_list) == 1:
            return dir_list[0].name
        return None

    def handle(self, *args, **options):
        try:
            language = options["lang"].strip('"')
        except AttributeError as e:
            language = self.detect_single_translation_language()

            if not language:
                raise RuntimeError('Please provide a language with the "--lang" parameter.') from e

        call_command("makemessages", "-l", language, "--no-location", "--no-wrap")

        file_path = f"{settings.LOCALE_PATHS[0]}/{language}/LC_MESSAGES/django.po"
        if not isfile(file_path):
            raise RuntimeError(f'PO file not found at "{file_path}".')

        with open(file_path, encoding="utf-8") as po_file:
            content_list = po_file.readlines()

        modified_content = [line for line in content_list if not line.startswith('"POT-Creation-Date:')]

        with open(file_path, "w", encoding="utf-8") as po_file:
            po_file.writelines(modified_content)
