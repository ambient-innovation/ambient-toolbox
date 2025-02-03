# Function registry with autodiscovery

Registration of functions is a neat pattern to loosen the coupling between certain areas of your application. Instead of
importing a function, the function registers itself in a central registry. If this function is deleted, the registration
will stop without any required changes in other parts of your application.

Common examples are celery tasks, which are registered with a `@celery` decorator.

## Basic example

Set `AMBIENT_TOOLBOX_AUTODISCOVER_ENABLED=True` in your Django settings file.

That's how you register a function:

```python
# my_app/my_group.py
from ambient_toolbox.autodiscover import function_registry


@function_registry.register_function(registry_group="my_group")
def my_function():
    pass
```

Note that the registry group defines the location where the autodiscovery will look for your decorated functions and classes.
So if you'd be implementing a notification feature, use `registry_group="notifications"` and put all your code in
`my_app/notifications.py` or respectively, in `my_app/notifications/my_file.py`.

And that's how you retrieve a group:

```python
from ambient_toolbox.autodiscover import function_registry

registered_callables = function_registry.get_registered_callables(
    registry_group="my_group"
)

# Execute registered callable
result = registered_callables[0]()
```

The "registry_group" parameter enables the developer to register different types of functions.

Imagine, you have notifications which you want to register, and in addition, you have an event queue where you want to
register handlers. Use different group names (aka namespaces) and you are good to go.

## Settings

### AMBIENT_TOOLBOX_APP_BASE_PATH

Queuebie needs to know where your project lives to detect local Django apps. It defaults to `settings.BASE_PATH`
but you can overwrite it with a string or a `Pathlib` object.

```python
from pathlib import Path

AMBIENT_TOOLBOX_APP_BASE_PATH = Path(__file__).resolve(strict=True).parent
```

### AMBIENT_TOOLBOX_CACHE_KEY

Queuebie will cache all detected message handlers in Django's default cache. The default cache key is "
toolbox_autodiscovery".
You can overwrite it with this variable.

```python
AMBIENT_TOOLBOX_CACHE_KEY = "my_very_special_cache_key"
```

### AMBIENT_TOOLBOX_LOGGER_NAME

Queuebie defines a Django logger with the default name "queuebie". If you want to rename that logger, you can set this
variable.

```python
AMBIENT_TOOLBOX_LOGGER_NAME = "my_very_special_logger"
```

Take care to use the same name in the logging configuration in your Django settings.
