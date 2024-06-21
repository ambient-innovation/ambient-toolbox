# Database Anonymisation

## Why we scrub

Nowadays, it is more important than ever to take care of data protection concerns. Especially in the European Union and
when you wish to be compliant to the [GDPR](https://en.wikipedia.org/wiki/General_Data_Protection_Regulation), you have
to take care of how you work with sensitive data.

During daily business it is often required to work with a production-like database dump - let's say, to fix a specific
bug. Creating a production-like dataset is far from trivial, and the most obvious approach is just dumping the
production database and installing it locally. Unfortunately, this exposes the (mostly) sensitive data to a various
number of ways to misplace it (physical laptop theft, digital computer breach and so on).

A common way to avoid these drawbacks is to replace the sensitive part of data with something that seems like the
original data but is mocked. This approach is called "scrubbing".

If you are interested in a deeper dive into this topic, feel free to read my
[article on Medium](https://medium.com/ambient-innovation/semantic-anonymisation-for-databases-via-django-88851f169081).

## What's happening here?

The regular [django-scrubber](https://pypi.org/project/django-scrubber/) package provides a django management command to
mock or fake all django models which have been declared as such.

Naturally, dumping the production database is a recurring task, and in most cases it requires a certain kind of pre-
and/or post-processing. Just picture how you would log into the system when all user data and therefore user credentials
are changed randomly?

That's why this package contains a neat wrapper for the original scrubber.

## How to use the wrapper

Just create a new python file somewhere in your application (`apps/core/scrubbing.py`) and create a class like this:

````python
class MyScrubbingService(AbstractScrubbingService):
    pre_scrub_functions = [
        'remove_some_data',
    ]

    post_scrub_functions = [
        'scrub_users',
        'delete_logs',
    ]

    def remove_some_data(self):
        pass

    def scrub_users(self):
        pass

    def delete_logs(self):
        pass
````

Note, that you can register methods for **pre- and post-processing**. Within the registered methods, you can access the
django ORM in the regular way.

*Note that only registered methods are being executed!*

Next, you need to create a django management command for your service to be able to call it from the CLI:

````python
from django.core.management.base import BaseCommand
from apps.core.services import PortalScrubbingService


class Command(BaseCommand):

    def handle(self, *args, **options):
        scrubbing_service = MyScrubbingService()
        scrubbing_service.process()
````

Create the file within one of your apps (`apps/core/management/commands/custom_scrub.py`).

### Pre-processing

A common use-case for pre-processing is the removal of big chunks of data to minimise the runtime of the scrubbing
process.

Another example could be that your data contains some kind of complicated business logic, and your system will break if
the data is anonymised in a trivial way. To prevent a mess, just do some magic on your dataset, and you are good to go.

### Post-processing

This is the more obvious and common way to use this wrapper.

As stated above, having a defined superuser (or other types of users, depending on your roles and permissions) can be a
big time saver for this process. At first, define all required users representing a relevant permission group, then
implement a method in your custom scrubbing service to create these users. Finally, ensure that the given credentials
are documented within the projects Readme file. Otherwise, people have to worry about roles and permissions every time.

Another widely used post-processing technique is truncating logging tables. In most cases, the logs are not relevant for
the developer or might even contain sensitive data. Furthermore, they tend to contain loads of data. Obviously, it is
nicer for everybody to work with smaller database dumps, so reducing the size as far as possible is recommended.

### Admin logs

By default, the logs of django admin are cleared when running the custom scrubber. If you want to avoid this, you can
set the attribute `keep_django_admin_log=True` within your scrubber class.

### Cleaning up django session data

By default, this service will remove all records from djangos session table `django_session`. Session data might contain
sensitive information and moreover a valid session key acts like a password. Furthermore, all users are anonymised so
the session data can't be accessed anyway. If you want to keep your session data, just disable it by setting the
attribute `keep_session_data=True`.

### Cleaning up scrubbing data

The original scrubber package creates a data pool for the anonymisation. This pool is usually quite big and therefore
causes your database to gain size. By default, this pool will be flushed after the custom scrubbing. If you want to keep
this data, just set the attribute `keep_scrubber_data=True` within your scrubber class.

### Helper method for user credentials

As stated above, a very common use-case is creating/editing anonymised users to be able to provide scrub-independent but
still anonymised user accounts. Therefore, this package provides a method `_get_hashed_default_password()` which will
turn a human-readable password into a hashed one.

By default, it will use the password "Admin0404!". If you want to use a different default password, feel free to
overwrite the class constant `DEFAULT_USER_PASSWORD`.

Here is an example:

````python

class MyScrubbingService(AbstractScrubbingService):
    post_scrub_functions = [
        'scrub_users',
        ...
    ]

    def scrub_users(self):
        # set the variable "SCRUBBER_DOMAIN" in your settings to your projects domain
        email = f'scrub-master@{settings.SCRUBBER_DOMAIN}'
        if not EmailUser.objects.filter(email=email).exists():
            EmailUser.objects.create(first_name='Scrub', last_name='Master',
                                     password=self._get_hashed_default_password(), email=email,
                                     is_active=True, is_superuser=True)

        self._logger.info(f'Created superuser "{email}" with password "{self.DEFAULT_USER_PASSWORD}".')

   ...

````

### Configuration

If you want to change the way the scrubber works, you can set various things in the settings. Please refer to
the [django-scrubber docs](https://github.com/RegioHelden/django-scrubber/blob/master/README.md).

Here is an example of how your configuration could look like:

````python
# Scrubber
SCRUBBER_ENTRIES_PER_PROVIDER = 10000
SCRUBBER_RANDOM_SEED = 456489135
SCRUBBER_APPS_LIST = LOCAL_APPS
SCRUBBER_DOMAIN = 'example.com'
````

Notes:

`LOCAL_APPS` is a list of all your local apps excluding third-party ones. Local apps and third-party apps are combined
in
`INSTALLED_APPS`.

`SCRUBBER_DOMAIN` is used for post-processing the users (see *"Helper method for user credentials"*).
