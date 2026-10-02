import sys

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """
    Detects ghost tables in the database that were likely created by Django but whose models
    have since been removed from the codebase without a corresponding database cleanup.
    """

    help = "Detects database tables no longer referenced by any Django model."

    def handle(self, *args, **options):
        table_names = set(connection.introspection.table_names())
        django_table_names = set(connection.introspection.django_table_names())
        possible_matches = table_names - django_table_names - {"django_migrations"}

        if len(possible_matches) == 0:
            return

        sys.stdout.write("The following tables might be left-overs and can be deleted:\n")
        for table in possible_matches:
            sys.stdout.write(f"* {table}\n")
