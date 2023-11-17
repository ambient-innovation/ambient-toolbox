[![PyPI release](https://img.shields.io/pypi/v/ambient-toolbox.svg)](https://pypi.org/project/ambient-toolbox/)
[![Downloads](https://static.pepy.tech/badge/ambient-toolbox)](https://pepy.tech/project/ambient-toolbox)
[![Coverage](https://img.shields.io/badge/Coverage-96.52%25-success)](https://github.com/ambient-innovation/ambient-toolbox/actions?workflow=CI)
[![Linting](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Coding Style](https://img.shields.io/badge/code%20style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Documentation Status](https://readthedocs.org/projects/ambient-toolbox/badge/?version=latest)](https://ambient-toolbox.readthedocs.io/en/latest/?badge=latest)

Python toolbox of Ambient Digital containing an abundance of useful tools and gadgets.

* [PyPI](https://pypi.org/project/ambient-toolbox/)
* [GitHub](https://github.com/ambient-innovation/ambient-toolbox)
* [Full documentation](https://ambient-toolbox.readthedocs.io/en/latest/index.html)
* Creator & Maintainer: [Ambient Digital](https://ambient.digital)

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

    ````
    INSTALLED_APPS = (
        ...
        'ambient_toolbox',
    )
     ````


- Apply migrations by running:

  `python ./manage.py migrate`





## Contribute

### Setup package for development

- Create a Python virtualenv and activate it
- Install "pip-tools" with `pip install -U pip-tools`
- Compile the requirements with `pip-compile --extra dev,drf,graphql,sentry,view-layer, -o requirements.txt pyproject.toml --resolver=backtracking`
- Sync the dependencies with your virtualenv with `pip-sync`

### Add functionality

- Create a new branch for your feature
- Change the dependency in your requirements.txt to a local (editable) one that points to your local file system:
  `-e /Users/workspace/ambient-toolbox` or via pip  `pip install -e /Users/workspace/ambient-toolbox`
- Ensure the code passes the tests
- Create a pull request

### Run tests

- Run tests
  ````
  pytest --ds settings tests
  ````

- Check coverage
  ````
  coverage run -m pytest --ds settings tests
  coverage report -m
  ````

### Git hooks (via pre-commit)

We use pre-push hooks to ensure that only linted code reaches our remote repository and pipelines aren't triggered in
vain.

To enable the configured pre-push hooks, you need to [install](https://pre-commit.com/) pre-commit and run once:

    pre-commit install -t pre-push -t pre-commit --install-hooks

This will permanently install the git hooks for both, frontend and backend, in your local
[`.git/hooks`](./.git/hooks) folder.
The hooks are configured in the [`.pre-commit-config.yaml`](templates/.pre-commit-config.yaml.tpl).

You can check whether hooks work as intended using the [run](https://pre-commit.com/#pre-commit-run) command:

    pre-commit run [hook-id] [options]

Example: run single hook

    pre-commit run ruff --all-files --hook-stage push

Example: run all hooks of pre-push stage

    pre-commit run --all-files --hook-stage push

### Update documentation

- To build the documentation run: `sphinx-build docs/ docs/_build/html/`.
- Open `docs/_build/html/index.html` to see the documentation.

### Translation files

If you have added custom text, make sure to wrap it in `_()` where `_` is
gettext_lazy (`from django.utils.translation import gettext_lazy as _`).

How to create translation file:

* Navigate to `ambient-toolbox`
* `python manage.py makemessages -l de`
* Have a look at the new/changed files within `ambient_toolbox/locale`

How to compile translation files:

* Navigate to `ambient-toolbox`
* `python manage.py compilemessages`
* Have a look at the new/changed files within `ambient_toolbox/locale`

### Publish to ReadTheDocs.io

- Fetch the latest changes in GitHub mirror and push them
- Trigger new build at ReadTheDocs.io (follow instructions in admin panel at RTD) if the GitHub webhook is not yet set
  up.

### Publish to PyPi

- Update documentation about new/changed functionality

- Update the `Changelog`

- Increment version in main `__init__.py`

- Create pull request / merge to master

- This project uses the flit package to publish to PyPI. Thus publishing should be as easy as running:
  ```
  flit publish
  ```

  To publish to TestPyPI use the following ensure that you have set up your .pypirc as
  shown [here](https://flit.readthedocs.io/en/latest/upload.html#using-pypirc) and use the following command:

  ```
  flit publish --repository testpypi
  ```

### Maintenance

Please note that this package supports the [ambient-package-update](https://pypi.org/project/ambient-package-update/).
So you don't have to worry about the maintenance of this package. All important configuration and setup files are
being rendered by this updater. It works similar to well-known updaters like `pyupgrade` or `django-upgrade`.

To run an update, refer to the [documentation page](https://pypi.org/project/ambient-package-update/)
of the "ambient-package-update".
