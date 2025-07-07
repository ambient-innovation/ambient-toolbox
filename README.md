[![PyPI release](https://img.shields.io/pypi/v/ambient-toolbox.svg)](https://pypi.org/project/ambient-toolbox/)
[![Downloads](https://static.pepy.tech/badge/ambient-toolbox)](https://pepy.tech/project/ambient-toolbox)
[![Coverage](https://img.shields.io/badge/Coverage-73.21%25-success)](https://github.com/ambient-innovation/ambient-toolbox/actions?workflow=CI)
[![Linting](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Coding Style](https://img.shields.io/badge/code%20style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Documentation Status](https://readthedocs.org/projects/ambient-toolbox/badge/?version=latest)](https://ambient-toolbox.readthedocs.io/en/latest/?badge=latest)

Python toolbox of Ambient Digital containing an abundance of useful tools and gadgets.

* [PyPI](https://pypi.org/project/ambient-toolbox/)
* [GitHub](https://github.com/ambient-innovation/ambient-toolbox)
* [Full documentation](https://ambient-toolbox.readthedocs.io/en/latest/index.html)
* Creator & Maintainer: [Ambient Digital](https://ambient.digital/)

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

## Installation

- Install the package via pip:

  `pip install ambient-toolbox`

  or via pipenv:

  `pipenv install ambient-toolbox`

- Add module to `INSTALLED_APPS` within the main django `settings.py`:

```python
INSTALLED_APPS = (
    # ...
    "ambient_toolbox",
)
```

- Apply migrations by running:

  `python ./manage.py migrate`

### Publish to ReadTheDocs.io

- Fetch the latest changes in GitHub mirror and push them
- Trigger new build at ReadTheDocs.io (follow instructions in admin panel at RTD) if the GitHub webhook is not yet set
  up.

### Publish to PyPi

- Update documentation about new/changed functionality

- Update the `Changelog`

- Increment version in main `__init__.py`

- Create pull request / merge to master

- This project uses the flit package to publish to PyPI. Thus, publishing should be as easy as running:
  ```
  flit publish
  ```

  To publish to TestPyPI use the following to ensure that you have set up your .pypirc as
  shown [here](https://flit.readthedocs.io/en/latest/upload.html#using-pypirc) and use the following command:

  ```
  flit publish --repository testpypi
  ```

### Maintenance

Please note that this package supports the [ambient-package-update](https://pypi.org/project/ambient-package-update/).
So you don't have to worry about the maintenance of this package. This updater is rendering all important
configuration and setup files. It works similar to well-known updaters like `pyupgrade` or `django-upgrade`.

To run an update, refer to the [documentation page](https://pypi.org/project/ambient-package-update/)
of the "ambient-package-update".
