[![PyPI release](https://img.shields.io/pypi/v/ambient-toolbox.svg)](https://pypi.org/project/ambient-toolbox/)
[![Downloads](https://static.pepy.tech/badge/ambient-toolbox)](https://pepy.tech/project/ambient-toolbox)
[![Coverage](https://img.shields.io/badge/Coverage-100.0%25-success)](https://github.com/ambient-innovation/ambient-toolbox/actions?workflow=CI)
[![Linting](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Coding Style](https://img.shields.io/badge/code%20style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Documentation Status](https://readthedocs.org/projects/ambient-toolbox/badge/?version=latest)](https://ambient-toolbox.readthedocs.io/en/latest/?badge=latest)

Python toolbox of Ambient Digital containing an abundance of useful tools and gadgets.

[PyPI](https://pypi.org/project/ambient-toolbox/) | [GitHub](https://github.com/ambient-innovation/ambient-toolbox) | [Full documentation](https://ambient-toolbox.readthedocs.io/en/latest/index.html)

Creator & Maintainer: [Ambient Digital](https://ambient.digital/)

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

  or via uv:

  `uv add ambient-toolbox`

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

### Preparation and building

This package uses [uv](https://github.com/astral-sh/uv) for dependency management and building.

- Update documentation about new/changed functionality

- Update the `CHANGES.md`

- Increment version in main `__init__.py`

- Create pull request / merge to "master"

- This project uses uv to publish to PyPI. This will create distribution files in the `dist/` directory.

  ```bash
  uv build
  ```

### Publishing to PyPI

To publish to the production PyPI:

```bash
uv publish
```

To publish to TestPyPI first (recommended for testing):

```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

You can then test the installation from TestPyPI:

```bash
uv pip install --index-url https://test.pypi.org/simple/ ambient-package-update
```

### Maintenance

Please note that this package supports the [ambient-package-update](https://pypi.org/project/ambient-package-update/).
So you don't have to worry about the maintenance of this package. This updater is rendering all important
configuration and setup files. It works similar to well-known updaters like `pyupgrade` or `django-upgrade`.

To run an update, refer to the [documentation page](https://pypi.org/project/ambient-package-update/)
of the "ambient-package-update".
