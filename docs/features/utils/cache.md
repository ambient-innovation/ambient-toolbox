## Cache

### Clear cache

The function ``clear_cache()`` wraps all the functionality needed to totally empty the django cache. Especially
convenient, if you put this function inside a management command, so you can flush the cache easily from the command
line:

````python
# my_app/management/commands/clear_cache.py

from django.core.management.base import BaseCommand
from ambient_toolbox.utils import clear_cache


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_cache()
````
