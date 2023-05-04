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

If you want to keep track of object ownership automatically, you can use the `CurrentUserMiddleware`.
Just make sure, you'll insert it **after** djangos `AuthenticationMiddleware`:

````python
MIDDLEWARE = (
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ambient_toolbox.middleware.current_user.CurrentUserMiddleware',
)
````

Using this middleware will automatically and thread-safe keep track of the ownership of all models,
which derive from `CommonInfo`.
