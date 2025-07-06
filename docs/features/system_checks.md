# System checks

## Model field naming conventions

Inspired
by [Luke Plants article](https://lukeplant.me.uk/blog/posts/enforcing-conventions-in-django-projects-with-introspection/),
this package implements a system check to ensure that all custom DateField and DateTimeField are named uniformly.

By default, it requires for DateFields to end on `_date` and DateTimeFields on `_at`.

It's straightforward to register this system check in your project.

````python
# apps/common/apps.py
from ambient_toolbox.system_checks.model_field_name_conventions import check_model_time_based_fields

from django.apps import AppConfig
from django.core.checks import register


class CommonConfig(AppConfig):
    name = "apps.common"
    verbose_name = "Common"

    def ready(self):
        register(check_model_time_based_fields)
````

You can configure which field name endings are allowed by setting these variables in your global Django settings file.

````python
# apps/config/settings.py

ALLOWED_MODEL_DATETIME_FIELD_ENDINGS = ["_at"]
ALLOWED_MODEL_DATE_FIELD_ENDINGS = ["_date"]
````

Make sure that you provide a list of your local apps (non-third-party ones) like this:

````python
# Main Django settings.py
LOCAL_APPS = (
    "myapp",
    "other_app",
)
````

## Model relation naming conventions

If you create a relation between two models (ForeignKey, ManyToMany, OneToOne), Django will name this relation with
the somehow obscure `*_set` name.

Since a well-chosen related name, either on the field itself or on the model meta-option "default_related_name", this
system check encourages you to set one of these attributes. Explicit is better than implicit.

It's straightforward to register this system check in your project.

````python
# apps/common/apps.py
from ambient_toolbox.system_checks.model_relation_conventions import check_model_related_names_for_related_name

from django.apps import AppConfig
from django.core.checks import register


class CommonConfig(AppConfig):
    name = "apps.common"
    verbose_name = "Common"

    def ready(self):
        register(check_model_related_names_for_related_name)
````

Make sure that you provide a list of your local apps (non-third-party ones) like this:

````python
# Main Django settings.py
LOCAL_APPS = (
    "myapp",
    "other_app",
)
````
