from os.path import isfile

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Wrapper command for "makemessages" to remove "POT-Creation-Date:" which will cause countless merge conflicts.
    """

    def add_arguments(self, parser):
        parser.add_argument("--lang", type=str)

    def handle(self, *args, **options):
        try:
            language = options["lang"].strip('"')
        except AttributeError as e:
            raise RuntimeError('Please provide a language with the "--lang" parameter.') from e

        call_command("makemessages", "-l", language, "--no-location", "--no-wrap")

        file_path = settings.LOCALE_PATHS[0] / f"{language}/LC_MESSAGES/django.po"
        if not isfile(file_path):
            raise RuntimeError(f'PO file not found at "{file_path}".')

        with open(file_path, encoding="utf-8") as po_file:
            content_list = po_file.readlines()

        modified_content = [line for line in content_list if not line.startswith('"POT-Creation-Date:')]

        with open(file_path, "w", encoding="utf-8") as po_file:
            po_file.writelines(modified_content)
