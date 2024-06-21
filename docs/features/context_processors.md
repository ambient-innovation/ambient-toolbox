# Context processors

## Server Settings

The function ``server_settings()`` puts the variables `DEBUG_MODE` and `SERVER_URL` in every django template.

Register the context manager like this in your global settings file:

````python
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'ambient_toolbox.context_processors.server_settings',
            ]

````

Afterwards, make sure that in the django settings the variables ``DEBUG`` and `SERVER_URL` are set.
