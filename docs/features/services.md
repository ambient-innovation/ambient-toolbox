# Services

## Semantic anonymisation for databases

### Motivation

Since the arrival of the European General Data Protection Regulation (GDPR) on May 25th 2018 at the latest, people started
worrying about how to handle sensitive data.

One of the main issues being addressed in GDPR is that if you store (or process) personal data of some kind, there
needs to be a justification why you do it. Furthermore, if you lose personal data of some kind, this needs to be
reported and made public. Usually a thing you want to avoid at all costs.

Therefore, — in theory — only a carefully selected number of administrators get access to the highly sensitive database.
But in practice you need a valid dataset for your test and staging server, your developers need one to work on locally
etc. If you want to read up a little more about the background, have a look at our
[article on Medium](https://medium.com/ambient-innovation/semantic-anonymisation-for-databases-via-django-88851f169081).

### Implementation

Working frequently in the django ecosystem, we found the django-scrubber package at some point in 2018. The great thing
about that tool is, that you can define all the fields which contain sensitive data and not just hash or empty them but
fill it with data having the same meaning as your production state.

Imagine, we have a django model for your customer data:

````python
# models.py

from django.db import models

class Customer(models.Model):
    first_name = models.CharField('First name', max_length=60)
    last_name = models.CharField('Last name', max_length=60)
    last_login = models.DateTimeField('Last login'))
````

If we take a closer look, we can see that the fields `first_name` and `last_name` contain sensitive data
whereas `last_login` is quite uncritical.

With django-scrubber, we can define a subclass within the model like this:

````python
# models.py

from django.db import modelsclass Customer(models.Model):
    ....

    class Scrubbers:
        first_name = scrubbers.Faker('first_name')
        last_name = scrubbers.Faker('last_name')
````

If we now run the management command scrub_data provided by scrubber, the package knows which fields to handle and how.
When you anonymise the dataset, scrubber will pick a random first name and a random last name for every customer record
you have in your database.

Scrubber utilises the Faker package which provides an abundance of helpful data types, like job descriptions, street
names and many more. And it can even provide localised (language-specific) data! You can read all about your options in
the Faker documentation.

In addition, scrubber itself provides a handful of useful tools like empty values or simply hashing the existing value
which you can read about (here)[https://github.com/RegioHelden/django-scrubber/blob/master/README.md]. A really nice
feature I would like to point out here is the value-casting. Faker only generates strings which the django ORM will not
save in a field type different from char or text field. Scrubber tries to cast the faked values, so they fit to the
declaration in the django model.

### Custom scrubber class

Usually you want as little hassle as possible when creating an anonymised dump. So manipulating all those special cases
as mentioned above and afterwards creating test users, forwarding credentials etc. is a thing you surely want to avoid.

For this reason we implemented an abstract class called AbstractScrubbingService:

````python
# services.py

from ambient_toolbox.services.custom_scrubber import AbstractScrubbingService

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

The service wraps the general scrubbing command and at the end truncates the scrubber data table. This table contains
preprocessed information to speed up the scrubbing process. You do not need it afterwards, though. We do this so the
database will be as small as possible for any kind of export.

Furthermore, you can create functions for handling data in any way which run before or after the scrubbing. You can see
this in the example above. Only register the functions in the class attributes `pre_scrub_functions` or
`post_scrub_functions` and implement it. Done!

Finally, you need to create a new management command called `custom_scrub`. Here is an example implementation:

````python
# custom_scrub.py

from django.core.management.base import BaseCommand
from apps.core.services import MyScrubbingService

class Command(BaseCommand):
    def handle(self, *args, **options):
        scrubbing_service = MyScrubbingService()
        scrubbing_service.process()
````
