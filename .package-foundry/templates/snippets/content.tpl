## Features

* Useful classes and mixins for Django admin
* Coverage script for GitLab
* Extensions for DRF and GraphQL
* Mailing backends for Django
* Management commands for validating a projects test structure
* Object ownership tracking with timestamping
* Pattern for improved workflow with Django ORM
* Helper and util functions for many different use-cases
* Sentry plugins
* django-scrubber wrapper class
* Mixins and test classes for django (class-based) views

# Migration from "ai_django_core"

This package was previously known as [ai_django_core](https://pypi.org/project/ai-django-core/). Due to the
misleading nature of the name, we chose to rename it with something more meaningful.

The migration is really simple, just:

* Install ambient-toolbox and remove the dependency to ai-django-core
* Search and replace all usages of `from ai_django_core...` to `from ambient_toolbox...`
* The class-based mail functionality was moved to a separate package called
[django-pony-express](https://pypi.org/project/django-pony-express/).
