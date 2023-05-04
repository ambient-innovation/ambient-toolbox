# Query Selectors

Django is a great framework but the code tends to get messy as time passes by and the project
grows. [HackSoft](https://github.com/HackSoftware/Django-Styleguide#selectors) has invented a pattern called "Selectors"
which takes care of calling ORM methods everywhere and thinking in (and encapsulating) use-cases instead of using the
ORM directly and not DRY.

In addition to this the company [WirBauenDigital](https://www.wirbauen.digital/) created a coding style which enforces
all Custom QuerySet (CQS) methods to be as atomic as possible. These CQS methods will be (re-)used in any place
throughout your system.

Combining these approaches with the [Ambient Digital](https://ambient.digital) style to separate CQS and managers in a
very strict way:

* CQS methods will always return a QuerySet
* They NEVER alter the data, just fetch it

## Definition

The result of this blend is a pattern we'd like to introduce as "Query Selectors". These selectors follow some rules:

A query selector...

* is a method or function which represents a single specific use-case ("fetch all active users who like beer")
* has a well-defined in- and output and no "magic" (for example, some functionality provided by its class)
* can be registered in the model to have a django-esque way of calling
  it (`MyModel.selectors.active_users_liking_beer()`)

## Example

Here you'll see how a selector class could look like. Note, that `is_active()` and `likes_beverages()` are CQS methods
defined within `UserQuerySet` which is registered in the `UserManager`.

```python
# my_app/selectors/user.py

from ambient_toolbox.selectors.base import Selector


class UserSelector(Selector):
    def active_users_liking_beer(self):
        """
        Fetches a list of active users who like to drink beer.
        """
        return self.model.objects.is_active().likes_beverages(beverage_list=['beer'])
```

Here is an example on how to register a selector within a model.

```python
# my_app/models.py

from django.db import models


class User(models.Model):
    ...

    objects = UserManager()
    selectors = UserSelector()
```

To complete the example, we'll add the CQS and manager as well:

```python
# my_app/managers/user.py

from django.db.models import manager


class UserQuerySet(manager.QuerySet):
    """
    Custom queryset for the "User" clas
    """

    def is_active(self):
        """
        Get all users who have the active flag set to "True"
        """
        return self.filter(is_active=True)

    def likes_beverages(self, beverage_list: list[str]):
        """
        Gets all users who have set at least one of the given list as their favourite beverage
        """
        return self.filter(beverages__name__in=beverage_list)


class UserManager(manager.Manager):
    def active_users_liking_beer(self):
        """
        Fetches a list of active users who like to drink beer.
        """
        return self.model.objects.is_active().likes_bevarages(beverage_list=['beer'])
```

## Remarks

* Take care that the current selector class inherits from the Django manager. This is a workaround to inject the current
  model class into the selector to avoid circular dependency errors and access the model manager/CQS via `self.model.*`.
  This means that Django will think you already have a custom manager, and you have to register a real custom manager.
  If you follow the given pattern, you need one anyway so that shouldn't be an issue. Nevertheless, if you leave one
  out, you'll get a weird error because Django will not create a default one.

## Permissions & Visibility

Similar to the manager section in this documentation, you can use a neat pattern for handling basic object visibility
with a mixin `AbstractUserSpecificSelectorMixin`. This mixin provides three methods: `visible_for()`,
`editable_for()` and `deletable_for()`. Each method needs to be implemented per selector class like this:

```python
# my_app/selector/mymodel.py

from ambient_toolbox.selectors.base import Selector
from ambient_toolbox.selectors.permission import AbstractUserSpecificSelectorMixin

class MyModelSelector(AbstractUserSpecificSelectorMixin, Selector):

    def visible_for(self, user):
        ...

    def editable_for(self, user):
        ...

    def deletable_for(self, user):
        ...
```
