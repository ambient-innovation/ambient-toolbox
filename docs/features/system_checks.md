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

## Atomic docs

The "atomic docs" pattern keeps documentation modular: a main README contains links to individual markdown files in a
docs directory. This system check ensures that no markdown file in the docs directory is forgotten or unlinked in the
README, keeping documentation discoverable and preventing orphaned docs from accumulating.

It's straightforward to register this system check in your project.

````python
# apps/common/apps.py
from ambient_toolbox.system_checks.atomic_docs import check_atomic_docs

from django.apps import AppConfig
from django.core.checks import register


class CommonConfig(AppConfig):
    name = "apps.common"
    verbose_name = "Common"

    def ready(self):
        register(check_atomic_docs)
````

You can configure the check by setting these variables in your global Django settings file.

````python
# apps/config/settings.py

# Project root for resolving relative paths (defaults to settings.BASE_DIR)
ATOMIC_DOCS_BASE_DIR = BASE_DIR

# Docs directory, relative to ATOMIC_DOCS_BASE_DIR (defaults to "docs")
ATOMIC_DOCS_DIR = "docs"

# README file path, relative to ATOMIC_DOCS_BASE_DIR (defaults to "README.md")
ATOMIC_DOCS_README_PATH = "README.md"
````
