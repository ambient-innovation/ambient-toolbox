import sys

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """
    Script to detect ghost tables.
    Ghost tables are tables which were probably created by Django,
    removed in the codebase but never removed in the database.
    """

    def handle(self, *args, **options):
        table_names = set(connection.introspection.table_names())
        django_table_names = set(connection.introspection.django_table_names())
        possible_matches = table_names - django_table_names - {"django_migrations"}

        if len(possible_matches) == 0:
            return

        sys.stdout.write("The following tables might be left-overs and can be deleted:\n")
        for table in possible_matches:
            sys.stdout.write(f"* {table}\n")
