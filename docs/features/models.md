# Models

## Object ownership

If you are interested in the backgrounds of this part, you can have a look at Medium,
[we posted an article there some time ago](https://medium.com/ambient-innovation/automatic-and-reliable-handling-of-object-ownership-in-django-34d7ad9721e9).


### Abstract class

If you want to keep track of the creator, creation time, last modificator and last modification time,
you can use the abstract class `CommonInfo` like this:

````python
from ambient_toolbox.models import CommonInfo


class MyFancyModel(CommonInfo):
    ...
````

You then get four fields: `created_by`, `created_at`, `lastmodified_by`, `lastmodified_at`.

If you are interested in the details, just have a look at the code base.

Note, that those fields will be automatically added to the `update_fields` if you choose to update only a subset of
fields on saving your object. However, you can set the class attribute `ALWAYS_UPDATE_FIELDS` to `False`
on your model to disable this behavior.

### Automatic object ownership

If you want to keep track of object ownership automatically, you can use the `CurrentRequestMiddleware`:

````python
MIDDLEWARE = (
    ...
    'ambient_toolbox.middleware.current_user.CurrentRequestMiddleware',
    ...
)
````

Using this middleware will automatically and thread-safe keep track of the ownership of all models,
which derive from `CommonInfo`.
In asynchronous contexts, you may expect a small performance penalty as this
middleware does not state being `async_capable` yet.

### Django Admin integration

For an easy and worry-free integration, set up your admin classes using `CommonInfoAdminMixin` to automatically take care of
the ownership when adding or changing objects via the admin.

It automatically sets the four fields (`created_by`, `created_at`, `lastmodified_by`, `lastmodified_at`) to read-only
and ensures that on saving the current object, the creator and/or the last editor are stored correctly.


````python
from ambient_toolbox.admin.model_admins.mixins import CommonInfoAdminMixin

@admin.register(MyModel)
class MyModelAdmin(CommonInfoAdminMixin, admin.ModelAdmin):
    pass
````

Note, that you can derive from this class and overwrite the `get_user_obj()` method if your ownership doesn't use the
default Django user object. This might be the case if you work with a OneToOne relation between the default `User` and
your custom one.

#### Limitations

Note that this package doesn't provide a mixin for InlineAdmins. But when you install the middleware, this shouldn't be
necessary anyway.
