# Clean-up

## Detect "forgotten" tables

Forgotten or ghost tables are tables which were created by Django migrations but then removed in the code. Django will
not necessarily remove tables when deleting models. Adam Johnson wrote
a [neat snippet](https://adamj.eu/tech/2024/11/21/django-tables-without-models/) to detect such tables.

This package provides a management command to neatly list those tables in the command-line.

```shell
python ./manage.py detect_ghost_tables

> The following tables might be left-overs and can be deleted:
> * invalid_table
```
