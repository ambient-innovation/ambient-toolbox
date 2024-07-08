# Translations

## "makemessages" wrapper management command

Working with translations can be tedious. If you don't have any checks in your pipeline, ever second time, you'll forget
to execute `manage.py makemessages`. Furthermore, you are enormously prone to merge conflicts because the file will be
time-stamped and the location comments can change very easily.

Therefore, we've created the management command `create_translation_file`, which will help you as follows:

> `python manage.py create_translation_file --lang en`

* The management command will call `makemessages` with --no-location to avoid cluttering your `*.po` files with
  easy-to-cause merge conflict reasons
* The management command will call `makemessages` with --no-wrap to show translations in a single line. This helps when
  comparing the po file.
* The management command will remove the `POT-Creation-Date:` header from the po-file to remove a source for merge
  conflicts.

## Pipeline checks

It makes a lot of sense to check your transaction file in the pipeline, to avoid forgotten or left-over translations.

This toolbox provides a management command to validate the integrity of your PO files.

The command will check all PO files from all active languages in the Django settings (`LANGUAGES`).

> python ./manage.py validate_translation_file_integrity

The following cases are being covered:
* Fuzzy translations aren't allowed
* Commented-out translations aren't allowed
* Validate, that `manage.py makemessages` has been called before committing
* Validate, that all translations were actually translated
