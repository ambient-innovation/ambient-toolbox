# Mixins

## BleacherMixin

### Motivation

Sometimes it is necessary to allow the user to write HTML and save this in the database. Unfortunately this creates the
possibility to insert malicious content. A package called [bleach](https://pypi.org/project/bleach) can help with this
problem.

Keep in mind that django templates will automatically escape all HTML and script code it renders. So if you want to
allow the user to create custom HTML content, this content has to be marked as "safe" in the template. This will
deactivate the escaping - and will render every evil piece of code the user inserted (intentionally or not).

If you allow custom content to be rendered "safely", you should whitelist harmless HTML tags and attributes and remove
all possible dangers - and as we are working with django, we want to define this security layer on a single point in the
code to be sure that it won't be forgotten at any time.

### Model mixin

Therefore, we create the `BleacherMixin` which is used in the model like this.

```
class MyModel(BleacherMixin, models.Model):
    BLEACH_FIELD_LIST = ['my_html_field']

    my_field = models.IntegerField()
    my_html_field = models.TextField()
```

This will automatically bleach (meaning escape) all non-whitelisted HTML tags and attributes in the defined fields while
leaving the white-listed ones intact.

Technically the mixin bleaches the field on a model `safe()` call.

### Default settings

The default settings are as follows:

```
DEFAULT_ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style', 'id'],
    'a': ['href', 'rel'],
    'img': ['alt', 'src'],
}

DEFAULT_ALLOWED_TAGS = bleach.ALLOWED_TAGS + ['span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5',*
                                              'h6', 'img', 'div', 'u', 'br', 'blockquote']
```

### Customize whitelists

If you want to alter your whitelists, just add something similar to this in your global django `settings.py`:

```
# Bleach
BLEACH_ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style', 'id'],
    'a': ['href', 'rel', 'target'],
    'img': ['alt', 'src'],
}

BLEACH_ALLOWED_TAGS = ['span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                       'img', 'div', 'u', 'br', 'blockquote', 'strong', 'a']

```

### Limitations

As the mixin works by extending the models `safe()`-method, bleaching **will not** be applied on all storage operations
done directly by the database, like `MyModel.objects.all().update(my_html_field='I am malicious content!')`.

Take care, that you have to set `BLEACH_ALLOWED_TAGS`. Otherwise, all tags will be allowed.

## Models

### PermissionModelMixin

When working with the Django permissions system, it happens quite often that you have to create a permission which
doesn't belong to a real-world data model. For example, if you want to show a comparison between table A and B - to
which model you would add this permission?

To fix this handicap, you can use the `PermissionModelMixin` which will create an unmanaged model (no database table
being created) which has no default permissions. You can just add your favourite permissions there and have a nice and
clean place to start from.

````python
from django.db import models
from ambient_toolbox.mixins.models import PermissionModelMixin

class ComparisonMyModelAndOtherModelPermission(PermissionModelMixin, models.Model):
    class Meta:
        permissions = (
            ('view_comparison', 'Can view the comparison'),
        )
````

Note that you still have to create a migration so your newly created permissions will be inserted in your database.

Attention: If you only need your custom permissions and not the Django default ones (`add_*`, `change_*`, ...), you have
to set the meta attribute `default_permissions` to an empty tuple or list. Otherwise, they will be created. It is not
possible to use inheritance here, explained in this [Django ticket](https://code.djangoproject.com/ticket/29386).

### SaveWithoutSignalsMixin

When working with Django signals, you might run into the conceptual problem, that signals are being triggered on
`.save()` calls although you wish for them not to be called, or that you run into racing-conditions where one signal
edits data before another signal was supposed to prepare the data.
This might happen in large, ever-growing projects where it is wiser, to work with a quickfix,
instead of rethinking your projects whole architecture.

For this use-case, you can use the `SaveWithoutSignalsMixin` from which your model can inherit,
which will add a `.save_without_signals()` method to your models, disconnecting all signals,
saving the instance and then reconnecting the signals.

```python
# models.py
from django.db import models
from ambient_toolbox.mixins.models import SaveWithoutSignalsMixin

class MyModelWithAnnoyingSignals(SaveWithoutSignalsMixin, models.Model):
    pass

# another_file.py

...
my_model = MyModelWithAnnoyingSignals.objects.create()
my_model.save_without_signals()  # save method call without any signals being triggered
my_model.save()  # "normal" save method, which will trigger signals
```

## Validation

### CleanOnSaveMixin

If you are following the fat-model approach, it might be convenient to put some low-level validation in the models "
clean" method which will be automatically called when using forms (or therefore, django admin). Unfortunately, it is not
called on a regular model save. Just derive your model from the `CleanOnSaveMixin` mixin and your clean will be called
on every save. Note that it won't be called on bulk operations not targeting model save.

````python
from django.db import models
from ambient_toolbox.mixins.validation import CleanOnSaveMixin

class ModelWithCleanMixin(CleanOnSaveMixin, models.Model):
    def clean(self):
        # to your magic here
        pass
````
