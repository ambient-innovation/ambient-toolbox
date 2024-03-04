# Translations

## "makemessages" wrapper management command

Working with translations can be tedious. If you don't have any checks in your pipeline, ever second time, you'll forget
to execute `manage.py makemessages`. Furthermore, you are enormously prone to merge conflicts because the file will be
time-stamped and the location comments can change very easily.

Therefore, we've created the management command `create_translation_file`, which will help you as follows:

> python manage.py create_translation_file --lang en

* The management command will call `makemessages` with --no-location to avoid cluttering your `*.po` files with
  easy-to-cause merge conflict reasons
* The management command will call `makemessages` with --no-wrap to show translations in a single line. This helps when
  comparing the po file.
* The management command will remove the `POT-Creation-Date:` header from the po-file to remove a source for merge
  conflicts.

## Pipeline checks

It makes a lot of sense to check your transaction file in the pipeline, to avoid forgotten or left-over translations.

Here is a comprehensive example for the language "en":

```yml
# Check for fuzzy translations
- echo "Check for fuzzy translations"
- grep -q "#, fuzzy" ./locale/en/LC_MESSAGES/django.po && exit 1
# Check for left-over translations
- echo "Check for left-over translations"
- grep -q "#~" ./locale/en/LC_MESSAGES/django.po && exit 1
# Check if "makemessages" detects new translations
- python manage.py create_translation_file --lang en
# Checking for differences in translation file
- echo "Checking for differences in translation file"
- git diff --ignore-matching-lines=POT-Creation-Date --ignore-matching-lines=# --exit-code locale/
# Check if all translation strings have been translated
- echo "Check if all translation strings have been translated"
- msgattrib --untranslated ./locale/en/LC_MESSAGES/django.po | exit `wc -c`
```
